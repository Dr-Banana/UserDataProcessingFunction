import sys
import os
import json
import unittest
from unittest import TestCase
from unittest.mock import MagicMock, patch
import boto3
import moto
import json_input

# 添加项目根目录到 Python 路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from lambda_function import lambda_handler

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

    def test_api_connect_test(self):
        """
        Test API connection test functionality
        """
        # 使用 API_CONNECT_TEST 数据
        event = json_input.API_CONNECT_TEST

        # 调用 lambda_handler
        response = lambda_handler(event, None)

        # 验证响应
        self.assertEqual(response['statusCode'], 200)
        body = json.loads(response['body'])
        self.assertEqual(body, {'message': 'API connection test successful'})

    # 其他的测试方法...

    def tearDown(self):
        """
        Clean up test environment
        """
        # 清理测试环境...

if __name__ == '__main__':
    unittest.main()