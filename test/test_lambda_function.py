"""
# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

# Start of unit test code: tests/test_lambda_function.py
"""

import sys
import os
import json
from unittest import TestCase
from unittest.mock import MagicMock, patch

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import the Lambda handler
from lambda_function import lambda_handler

class TestLambdaFunction(TestCase):
    """
    Test class for the Lambda function
    """

    def setUp(self):
        """
        Set up test environment
        """
        # Set up environment variables if needed
        os.environ['ENDPOINT_NAME'] = 'https://95zkfcumvb.execute-api.us-east-1.amazonaws.com/default/UserDataProcessingFunction'
        os.environ['TABLE_NAME'] = 'TodoList'
        os.environ['OUTPUT_BUCKET_NAME'] = 'userdata-processing-output'

    @patch('lambda_function.SageMakerHandler')
    @patch('lambda_function.DynamoDBHandler')
    @patch('lambda_function.save_to_s3')
    def test_lambda_handler_api_connection(self, mock_save_to_s3, mock_dynamodb_handler, mock_sagemaker_handler):
        """
        Test if the lambda_handler can be called without errors
        """
        # Mock the SageMaker prediction
        mock_sagemaker_instance = MagicMock()
        mock_sagemaker_instance.predict.return_value = [{'generation': {'content': '{"result": "mocked result"}'}}]
        mock_sagemaker_handler.return_value = mock_sagemaker_instance

        # Create a sample event
        event = {
            'body': json.dumps({
                "action": "predict",
                "input_text": "I will have dinner with mom today afternoon at 7pm near downtown. Tomorrow morning at 9am, I have a meeting with the marketing team in the office. On Wednesday, there is a doctor's appointment at 3pm at the clinic. ",
                "UserID": "1e026504-b625-4738-9e5d-e472c41510e4"
            })
        }

        # Call the lambda_handler
        response = lambda_handler(event, None)

        # Check if the response is as expected
        self.assertEqual(response['statusCode'], 200)
        self.assertIn('content', json.loads(response['body']))

        # Verify that the mocked methods were called
        mock_sagemaker_instance.predict.assert_called_once()
        mock_save_to_s3.assert_called_once()
        mock_dynamodb_handler.return_value.update_item.assert_called_once()

    def tearDown(self):
        """
        Clean up after tests
        """
        # Remove environment variables if needed
        if 'ENDPOINT_NAME' in os.environ:
            del os.environ['ENDPOINT_NAME']
        if 'TABLE_NAME' in os.environ:
            del os.environ['TABLE_NAME']
        if 'OUTPUT_BUCKET_NAME' in os.environ:
            del os.environ['OUTPUT_BUCKET_NAME']

# End of unit test code