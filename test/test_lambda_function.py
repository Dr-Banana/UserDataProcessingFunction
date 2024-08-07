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
        self.conversation_table = self.dynamodb.create_table(
            TableName=CONVERSATION_TABLE_NAME,
            KeySchema=[{'AttributeName': 'UserID', 'KeyType': 'HASH'}, {'AttributeName': 'ConversationID', 'KeyType': 'RANGE'}],
            AttributeDefinitions=[{'AttributeName': 'UserID', 'AttributeType': 'S'}, {'AttributeName': 'ConversationID', 'AttributeType': 'S'}],
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
        eventID = "test-event"
        content = {'event_1': {'brief': 'Test event', 'time': '10:00', 'place': 'Office', 'people': 'Team', 'date': '2024-06-28'}}
        
        save_result_to_s3(user_id, eventID, content)
        
        # 验证文件是否被保存到 S3
        s3_object = self.s3_client.get_object(Bucket=OUTPUT_BUCKET_NAME, Key=f'{user_id}/{eventID}.json')
        saved_content = json.loads(s3_object['Body'].read().decode('utf-8'))
        
        self.assertEqual(saved_content, content, "Content saved to S3 does not match the original content")

    def test_save_result_to_dynamodb(self):
        """
        Test saving results to DynamoDB
        """
        user_id = 'test-user'
        conversation_id = "test-conversation-id"
        content = {'event_1': {'brief': 'Test event', 'time': '10:00', 'place': 'Office', 'people': 'Team', 'date': '2024-06-28'}}
        
        save_result_to_dynamodb(user_id, conversation_id, content)

        response = self.conversation_table.get_item(
            Key={
                'UserID': user_id,
                'ConversationID': conversation_id
            }
        )
        
        if 'Item' in response:
            saved_content = response['Item']['Content']
            self.assertEqual(saved_content, content, "Content saved to DynamoDB does not match the original content")
        else:
            self.fail("Expected data not found in DynamoDB")
            
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

    def tearDown(self):
        """
        Clean up test environment
        """
        # 清理 S3 bucket
        bucket = self.s3_resource.Bucket(OUTPUT_BUCKET_NAME)
        bucket.objects.all().delete()
        bucket.delete()

        # 清理 DynamoDB 表
        self.conversation_table.delete()

if __name__ == '__main__':
    unittest.main()