import sys
import os
import json
import unittest
from unittest import TestCase
from unittest.mock import MagicMock, patch
import boto3
import moto
from botocore.exceptions import ClientError

# 添加项目根目录到 Python 路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from lambda_function import lambda_handler

@moto.mock_apigateway
class TestLambdaFunction(TestCase):
    """
    Test class for the UserDataProcessingFunction Lambda
    """

    def setUp(self):
        """
        Set up test environment
        """
        self.api_id = '6inctbtbvk'
        self.stage_name = 'dev'
        self.resource_path = '/UserDataProcessingFunction'
        
        # 设置 moto mock
        self.apigateway_mock = moto.mock_apigateway()
        self.apigateway_mock.start()
        
        # 创建 API Gateway client
        self.api_client = boto3.client('apigateway', region_name='us-east-1')
        
        # 创建模拟的 API
        self.create_mock_api()

    def create_mock_api(self):
        """
        Create a mock API in API Gateway
        """
        # 创建 API
        api = self.api_client.create_rest_api(name='TestAPI')
        self.api_id = api['id']
        
        # 获取根资源 ID
        resources = self.api_client.get_resources(restApiId=self.api_id)
        root_id = [resource for resource in resources['items'] if resource['path'] == '/'][0]['id']
        
        # 创建资源
        resource = self.api_client.create_resource(
            restApiId=self.api_id,
            parentId=root_id,
            pathPart='UserDataProcessingFunction'
        )
        
        # 创建方法
        self.api_client.put_method(
            restApiId=self.api_id,
            resourceId=resource['id'],
            httpMethod='POST',
            authorizationType='NONE'
        )

    def test_api_integration(self):
        """
        Test API integration
        """
        # 准备测试请求
        test_request = {
            "action": "test",
            "input_text": "Test input",
            "UserID": "test-user"
        }

        try:
            # 获取资源 ID
            resources = self.api_client.get_resources(restApiId=self.api_id)
            resource_id = next(resource['id'] for resource in resources['items'] if resource['path'] == self.resource_path)

            # 调用 API
            response = self.api_client.test_invoke_method(
                restApiId=self.api_id,
                resourceId=resource_id,
                httpMethod='POST',
                body=json.dumps(test_request)
            )

            # 验证响应
            self.assertEqual(response['status'], 200)
            body = json.loads(response['body'])
            self.assertEqual(body, {"message": "API connection test successful"})

        except ClientError as e:
            self.fail(f"API call failed: {str(e)}")

    @patch('lambda_function.predict')
    def test_lambda_handler(self, mock_predict):
        """
        Test lambda handler function
        """
        mock_predict.return_value = {"result": "mocked result"}

        event = {
            "body": json.dumps({
                "action": "predict",
                "input_text": "Test input",
                "UserID": "test-user"
            })
        }

        response = lambda_handler(event, None)

        self.assertEqual(response['statusCode'], 200)
        body = json.loads(response['body'])
        self.assertEqual(body, {'content': {"result": "mocked result"}})

    def tearDown(self):
        """
        Clean up test environment
        """
        self.apigateway_mock.stop()

if __name__ == '__main__':
    unittest.main()