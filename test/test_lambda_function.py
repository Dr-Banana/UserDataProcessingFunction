"""
# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

# Start of unit test code: test/test_lambda_function.py
"""

import sys
import os
import json
from unittest import TestCase
from unittest.mock import MagicMock, patch
import boto3
import moto
import requests

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import the Lambda handler and other necessary components
from lambda_function import lambda_handler, predict, save_result_to_s3, save_result_to_dynamodb
from config.config import ENDPOINT_NAME, TABLE_NAME, OUTPUT_BUCKET_NAME, PRESET_PROMPT, PARAMETERS
from utils.json_processor import process_json

@moto.mock_sagemaker
@moto.mock_s3
@moto.mock_dynamodb
class TestLambdaFunction(TestCase):
    """
    Test class for the Lambda function
    """

    def setUp(self):
        """
        Set up mocked AWS resources and environment variables
        """
        # Set up environment variables
        os.environ['ENDPOINT_NAME'] = ENDPOINT_NAME
        os.environ['TABLE_NAME'] = TABLE_NAME
        os.environ['OUTPUT_BUCKET_NAME'] = OUTPUT_BUCKET_NAME

        # Set up mocked S3
        self.s3 = boto3.client('s3', region_name='us-east-1')
        self.s3.create_bucket(Bucket=OUTPUT_BUCKET_NAME)

        # Set up mocked DynamoDB
        self.dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
        self.table = self.dynamodb.create_table(
            TableName=TABLE_NAME,
            KeySchema=[{'AttributeName': 'UserID', 'KeyType': 'HASH'}],
            AttributeDefinitions=[{'AttributeName': 'UserID', 'AttributeType': 'S'}],
            BillingMode='PAY_PER_REQUEST'
        )

    @patch('handlers.sagemaker_handler.SageMakerHandler')
    def test_predict(self, mock_sagemaker_handler):
        """
        Test the predict function
        """
        mock_sagemaker_handler.return_value.predict.return_value = {'event_1': {'brief': 'Some event'}}
        
        result = predict('Test input text')
        
        self.assertIn('event_1', result)
        mock_sagemaker_handler.return_value.predict.assert_called_once()

    @patch('handlers.sagemaker_handler.SageMakerHandler')
    def test_predict_error_handling(self, mock_sagemaker_handler):
        """
        Test the predict function's error handling
        """
        mock_sagemaker_handler.return_value.predict.side_effect = Exception("SageMaker error")
        
        with self.assertRaises(RuntimeError):
            predict('Test input text')
        
        mock_sagemaker_handler.return_value.predict.assert_called_once()

    def test_save_result_to_s3(self):
        """
        Test saving results to S3
        """
        user_id = 'test-user'
        content = {'event_1': {'brief': 'Test event'}}
        
        save_result_to_s3(user_id, content)
        
        s3_object = self.s3.get_object(Bucket=OUTPUT_BUCKET_NAME, Key=f'{user_id}/result.json')
        saved_content = json.loads(s3_object['Body'].read().decode('utf-8'))
        
        self.assertEqual(saved_content, content)

    def test_save_result_to_dynamodb(self):
        """
        Test saving results to DynamoDB
        """
        user_id = 'test-user'
        content = {'TodoList': {'event_1': {'brief': 'Test event'}}}
        
        save_result_to_dynamodb(user_id, content)
        
        item = self.table.get_item(Key={'UserID': user_id})['Item']
        
        self.assertEqual(item['TodoList'], content['TodoList'])

    @patch('lambda_function.predict')
    @patch('lambda_function.save_result_to_s3')
    @patch('lambda_function.save_result_to_dynamodb')
    def test_lambda_handler(self, mock_save_dynamodb, mock_save_s3, mock_predict):
        """
        Test the lambda_handler function
        """
        mock_predict.return_value = {'event_1': {'brief': 'Test event'}}
        
        event = {
            'body': json.dumps({
                'input_text': 'test input',
                'UserID': 'test-user',
                'action': 'predict'
            })
        }
        
        response = lambda_handler(event, None)
        
        self.assertEqual(response['statusCode'], 200)
        self.assertEqual(json.loads(response['body']), {'content': {'event_1': {'brief': 'Test event'}}})
        
        mock_predict.assert_called_once_with('test input')
        mock_save_s3.assert_called_once_with('test-user', {'event_1': {'brief': 'Test event'}})
        mock_save_dynamodb.assert_called_once_with('test-user', {'event_1': {'brief': 'Test event'}})

    @patch('lambda_function.predict')
    @patch('lambda_function.save_result_to_s3')
    @patch('lambda_function.save_result_to_dynamodb')
    def test_lambda_handler_api_gateway(self, mock_save_dynamodb, mock_save_s3, mock_predict):
        """
        Test the lambda_handler function with API Gateway input
        """
        mock_predict.return_value = {'event_1': {'brief': 'Dinner with mom'}, 'event_2': {'brief': 'Meeting with marketing team'}, 'event_3': {'brief': "Doctor's appointment"}}
        
        event = {
            'body': json.dumps({
                'action': 'predict',
                'input_text': "I will have dinner with mom today afternoon at 7pm near downtown. Tomorrow morning at 9am, I have a meeting with the marketing team in the office. On Wednesday, there is a doctor's appointment at 3pm at the clinic.",
                'UserID': '1e026504-b625-4738-9e5d-e472c41510e4'
            })
        }
        
        response = lambda_handler(event, None)
        
        self.assertEqual(response['statusCode'], 200)
        response_body = json.loads(response['body'])
        self.assertIn('content', response_body)
        self.assertIn('event_1', response_body['content'])
        self.assertIn('event_2', response_body['content'])
        self.assertIn('event_3', response_body['content'])
        
        mock_predict.assert_called_once()
        mock_save_s3.assert_called_once()
        mock_save_dynamodb.assert_called_once()

    def test_lambda_handler_invalid_input(self):
        """
        Test the lambda_handler function with invalid input
        """
        event = {
            'body': json.dumps({
                'input_text': '',
                'UserID': '',
                'action': 'predict'
            })
        }
        
        response = lambda_handler(event, None)
        
        self.assertEqual(response['statusCode'], 400)
        self.assertIn('Invalid input', json.loads(response['body'])['error'])

    def test_lambda_handler_invalid_action(self):
        """
        Test the lambda_handler function with invalid action
        """
        event = {
            'body': json.dumps({
                'input_text': 'test input',
                'UserID': 'test-user',
                'action': 'invalid_action'
            })
        }
        
        response = lambda_handler(event, None)
        
        self.assertEqual(response['statusCode'], 400)
        self.assertIn('Invalid action', json.loads(response['body'])['error'])

    @patch('utils.json_processor.process_json')
    def test_process_json(self, mock_process_json):
        """
        Test the process_json function
        """
        mock_llama_output = [{"generation": {"content": '{"event_1": {"brief": "Test event"}}'}}]
        expected_output = {"event_1": {"brief": "Test event"}}
        mock_process_json.return_value = expected_output

        result = process_json(mock_llama_output)

        self.assertEqual(result, expected_output)
        mock_process_json.assert_called_once_with(mock_llama_output)

    def tearDown(self):
        """
        Clean up mocked resources
        """
        self.s3.delete_bucket(Bucket=OUTPUT_BUCKET_NAME)
        self.table.delete()

def test_api_integration():
    """
    Integration test for the API endpoint
    """
    url = "https://95zkfcumvb.execute-api.us-east-1.amazonaws.com/default/UserDataProcessingFunction"
    payload = {
        "action": "predict",
        "input_text": "I will have dinner with mom today afternoon at 7pm near downtown. Tomorrow morning at 9am, I have a meeting with the marketing team in the office. On Wednesday, there is a doctor's appointment at 3pm at the clinic.",
        "UserID": "1e026504-b625-4738-9e5d-e472c41510e4"
    }
    
    response = requests.post(url, json=payload)
    
    assert response.status_code == 200
    response_body = response.json()
    assert 'content' in response_body
    assert 'event_1' in response_body['content']

# End of unit test code