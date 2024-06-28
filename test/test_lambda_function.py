import sys
import os
import json
import unittest
from unittest import TestCase
from unittest.mock import MagicMock, patch
import boto3
import moto
from test.json_input import ENDPOINT_CONNECT_TEST

# 添加项目根目录到 Python 路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from lambda_function import lambda_handler, predict

class TestLambdaFunction(TestCase):
    """
    Test class for the UserDataProcessingFunction Lambda
    """

    def setUp(self):
        """
        Set up test environment
        """
        # 设置其他的测试环境...

    # 其他的测试方法...

    def llama_endpoint_connect(self):
        """
        Test EndPoint connection test functionality
        """
        event = ENDPOINT_CONNECT_TEST
        response = lambda_handler(event, None)

        # 验证响应
        self.assertEqual(response['statusCode'], 200)
        body = json.loads(response['body'])
        self.assertEqual(body, {'message': 'ENDPOINT connection test successful'})

    @patch('lambda_function.SageMakerHandler')
    def llama_predict(self, mock_sagemaker_handler):
        """
        Test LLaMA model prediction
        """
        mock_llama_response = [
            {
                "generation": {
                    "content": json.dumps({
                        "event_1": {
                            "brief": "Meeting with team",
                            "time": "10:00 AM",
                            "place": "Conference Room",
                            "people": "Team members",
                            "date": "2024-06-28"
                        }
                    })
                }
            }
        ]
        mock_sagemaker_handler.return_value.predict.return_value = mock_llama_response

        # 调用 predict 函数
        result = predict("Schedule a team meeting for tomorrow at 10 AM in the conference room.")

        # 验证结果
        self.assertIsInstance(result, dict)
        self.assertIn('event_1', result)
        event = result['event_1']
        self.assertIsInstance(event, dict)
        self.assertIn('brief', event)
        self.assertIn('time', event)
        self.assertIn('place', event)
        self.assertIn('people', event)
        self.assertIn('date', event)

    def tearDown(self):
        """
        Clean up test environment
        """
        # 清理测试环境...

if __name__ == '__main__':
    unittest.main()