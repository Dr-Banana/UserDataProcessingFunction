import sys
import os
import json
import unittest
from unittest import TestCase
from unittest.mock import MagicMock, patch
import boto3
from moto.s3 import mock_s3
from moto.dynamodb import mock_dynamodb
from test.json_input import ENDPOINT_CONNECT_TEST, LLAMA_RESPONSE_TEST

# 添加项目根目录到 Python 路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from lambda_function import lambda_handler, predict, save_result_to_s3, save_result_to_dynamodb
from config.config import OUTPUT_BUCKET_NAME, TABLE_NAME
from moto.sagemaker import mock_sagemaker

@mock_sagemaker
@mock_s3
@mock_dynamodb
class TestLambdaFunction(TestCase):
    """
    Test class for the UserDataProcessingFunction Lambda
    """

    def setUp(self):
        """
        Set up test environment
        """
        # 创建模拟的 S3 bucket
        self.s3 = boto3.client('s3', region_name='us-east-1')
        self.s3.create_bucket(Bucket=OUTPUT_BUCKET_NAME)

        # 创建模拟的 DynamoDB 表
        self.dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
        self.table = self.dynamodb.create_table(
            TableName=TABLE_NAME,
            KeySchema=[{'AttributeName': 'UserID', 'KeyType': 'HASH'}],
            AttributeDefinitions=[{'AttributeName': 'UserID', 'AttributeType': 'S'}],
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
        content = {'event_1': {'brief': 'Test event', 'time': '10:00 AM'}}
        
        save_result_to_s3(user_id, content)
        
        s3_object = self.s3.get_object(Bucket=OUTPUT_BUCKET_NAME, Key=f'{user_id}/result.json')
        saved_content = json.loads(s3_object['Body'].read().decode('utf-8'))
        
        self.assertEqual(saved_content, content)

    def test_save_result_to_dynamodb(self):
        """
        Test saving results to DynamoDB
        """
        user_id = 'test-user'
        content = {'event_1': {'brief': 'Test event', 'time': '10:00 AM'}}
        
        save_result_to_dynamodb(user_id, content)
        
        response = self.table.get_item(Key={'UserID': user_id})
        saved_item = response['Item']
        
        self.assertEqual(saved_item['TodoList'], content)

    def tearDown(self):
        """
        Clean up test environment
        """
        self.s3_mock.stop()
        self.dynamodb_mock.stop()

if __name__ == '__main__':
    unittest.main()