import sys
import os
import json
import unittest
from unittest import TestCase
from unittest.mock import MagicMock, patch
import boto3
from moto import mock_s3, mock_dynamodb
from test.json_input import ENDPOINT_CONNECT_TEST, LLAMA_RESPONSE_TEST

# 添加项目根目录到 Python 路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from lambda_function import lambda_handler, predict, save_result_to_s3, save_result_to_dynamodb, handle_clarification
from config.config import OUTPUT_BUCKET_NAME, TODO_TABLE_NAME, CONVERSATION_TABLE_NAME
@mock_dynamodb
@mock_s3
class TestLambdaFunction(TestCase):
    """
    Test class for the UserDataProcessingFunction Lambda
    """

    def setUp(self):
        """
        Set up test environment
        """
        # 创建模拟的 S3 client 和 resource
        self.s3_client = boto3.client('s3', region_name='us-east-1')
        self.s3_resource = boto3.resource('s3', region_name='us-east-1')
        self.s3_client.create_bucket(Bucket=OUTPUT_BUCKET_NAME)

        # 创建模拟的 DynamoDB 表
        self.dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
        self.table = self.dynamodb.create_table(
            TableName=TODO_TABLE_NAME,
            KeySchema=[{'AttributeName': 'UserID', 'KeyType': 'HASH'}],
            AttributeDefinitions=[{'AttributeName': 'UserID', 'AttributeType': 'S'}],
            BillingMode='PAY_PER_REQUEST'
        )
        self.conversation_table = self.dynamodb.create_table(
            TableName=CONVERSATION_TABLE_NAME,
            KeySchema=[{'AttributeName': 'EventID', 'KeyType': 'HASH'}],
            AttributeDefinitions=[{'AttributeName': 'EventID', 'AttributeType': 'S'}],
            BillingMode='PAY_PER_REQUEST'
        )

    def test_llama_endpoint_connect(self):
        """
        Test EndPoint connection test functionality
        """
        event = ENDPOINT_CONNECT_TEST
        response = lambda_handler(event, None)

        try:
            self.assertEqual(response['statusCode'], 200, 
                f"Endpoint connection failed. Expected status code 200, but got {response['statusCode']}.")

            body = json.loads(response['body'])
            self.assertEqual(body, {'message': 'ENDPOINT connection test successful'}, 
                f"Unexpected response body. Got: {body}.")

        except KeyError as e:
            self.fail(f"Response is missing expected key: {e}.")
        except json.JSONDecodeError:
            self.fail(f"Failed to parse response body: {response.get('body', 'No body')}.")
        except AssertionError as e:
            self.fail(f"Endpoint connection test failed: {str(e)}.")

        print("Endpoint connection test passed successfully.")

    @patch('lambda_function.SageMakerHandler')
    def test_llama_predict(self, mock_sagemaker_handler):
        """
        Test LLaMA model prediction
        """
        mock_llama_response = LLAMA_RESPONSE_TEST
        mock_sagemaker_handler.return_value.predict.return_value = mock_llama_response

        result = predict("Schedule a team meeting for tomorrow at 10 AM in the conference room.")

        self.assertIsInstance(result, dict)
        self.assertIn('event_1', result)
        event = result['event_1']
        self.assertIsInstance(event, dict)
        self.assertIn('brief', event)
        self.assertIn('time', event)
        self.assertIn('place', event)
        self.assertIn('people', event)
        self.assertIn('date', event)

    def test_save_result_to_s3(self):
        """
        Test saving results to S3
        """
        user_id = 'test-user'
        content = {'event_1': {'brief': 'Test event', 'time': '10:00', 'place': 'Office', 'people': 'Team', 'date': '2024-06-28'}}
        
        save_result_to_s3(user_id, content)
        
        # 验证文件是否被保存到 S3
        s3_object = self.s3_client.get_object(Bucket=OUTPUT_BUCKET_NAME, Key=f'{user_id}/result.json')
        saved_content = json.loads(s3_object['Body'].read().decode('utf-8'))
        
        self.assertEqual(saved_content, content, "Content saved to S3 does not match the original content")

    def test_save_result_to_dynamodb(self):
        """
        Test saving results to DynamoDB
        """
        user_id = 'test-user'
        content = {'event_1': {'brief': 'Test event', 'time': '10:00', 'place': 'Office', 'people': 'Team', 'date': '2024-06-28'}}
        
        save_result_to_dynamodb(user_id, content)
        
        # 验证数据是否被保存到 DynamoDB
        item = self.table.get_item(Key={'UserID': user_id})['Item']
        
        self.assertEqual(item['TodoList'], content, "Content saved to DynamoDB does not match the original content")

    @patch('lambda_function.predict')
    @patch('lambda_function.save_result_to_s3')
    @patch('lambda_function.save_result_to_dynamodb')
    def test_handle_predict(self, mock_save_dynamodb, mock_save_s3, mock_predict):
        """
        Test the entire predict handling process
        """
        mock_predict.return_value = {'event_1': {'brief': 'Test event', 'time': '10:00', 'place': 'Office', 'people': 'Team', 'date': '2024-06-28'}}
        
        event = {
            'body': json.dumps({
                'action': 'predict',
                'input_text': 'Schedule a team meeting',
                'UserID': 'test-user'
            })
        }
        
        response = lambda_handler(event, None)
        
        self.assertEqual(response['statusCode'], 200)
        body = json.loads(response['body'])
        self.assertIn('content', body)
        
        mock_predict.assert_called_once_with('Schedule a team meeting')
        mock_save_s3.assert_called_once()
        mock_save_dynamodb.assert_called_once()

    @patch('lambda_function.download_json_from_s3')
    @patch('lambda_function.save_result_to_s3')
    @patch('lambda_function.save_result_to_dynamodb')
    @patch('lambda_function.dynamodb_handler')
    def test_handle_clarification(self, mock_dynamodb_handler, mock_save_s3, mock_download_s3, mock_save_dynamodb):
        user_id = 'test-user'
        conversation_id = 'test-conversation'
        missing_fields = ['time', 'place']
        updated_content = {'time': '10:00 AM', 'place': 'Conference Room'}
        current_content = {'event_1': {'brief': 'Test event', 'time': None, 'place': None, 'people': 'Team', 'date': '2024-06-28'}}

        mock_download_s3.return_value = json.dumps(current_content)
        mock_save_s3.return_value = None
        mock_save_dynamodb.return_value = None
        mock_dynamodb_handler.remove_ongoing_conversation.return_value = None

        response = handle_clarification(user_id, conversation_id, missing_fields, updated_content)

        self.assertEqual(response['statusCode'], 200)
        body = json.loads(response['body'])
        self.assertNotIn('missing_fields', body)
        self.assertIn('content', body)
        self.assertEqual(body['content'], {'event_1': {'brief': 'Test event', 'time': '10:00 AM', 'place': 'Conference Room', 'people': 'Team', 'date': '2024-06-28'}})

        mock_download_s3.assert_called_once_with(self.s3_client, OUTPUT_BUCKET_NAME, f"{user_id}/{conversation_id}.json")
        mock_save_s3.assert_called_once_with(user_id, conversation_id, {'event_1': {'brief': 'Test event', 'time': '10:00 AM', 'place': 'Conference Room', 'people': 'Team', 'date': '2024-06-28'}})
        mock_save_dynamodb.assert_called_once_with(user_id, {'event_1': {'brief': 'Test event', 'time': '10:00 AM', 'place': 'Conference Room', 'people': 'Team', 'date': '2024-06-28'}})
        mock_dynamodb_handler.remove_ongoing_conversation.assert_called_once_with(user_id)

    def tearDown(self):
        """
        Clean up test environment
        """
        # 清理 S3 bucket
        bucket = self.s3_resource.Bucket(OUTPUT_BUCKET_NAME)
        bucket.objects.all().delete()
        bucket.delete()

        # 清理 DynamoDB 表
        self.table.delete()

if __name__ == '__main__':
    unittest.main()