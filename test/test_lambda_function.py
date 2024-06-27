import json
import unittest
from unittest.mock import patch
import boto3
import os
from lambda_function import lambda_handler

class TestLambdaFunction(unittest.TestCase):

    def setUp(self):
        # 设置集成测试所需的 API Gateway 客户端
        self.api_client = boto3.client('apigateway', region_name='us-east-1')
        self.api_id = os.environ.get('API_GATEWAY_ID', '6inctbtbvk')
        self.stage_name = os.environ.get('API_STAGE_NAME', 'dev')
        self.resource_path = '/UserDataProcessingFunction'

    # 单元测试
    @patch('lambda_function.logger')
    def test_lambda_handler_unit(self, mock_logger):
        # 准备测试事件
        event = {
            "body": json.dumps({
                "action": "test"
            })
        }
        
        # 调用 Lambda 函数
        response = lambda_handler(event, None)
        
        # 验证响应
        self.assertEqual(response['statusCode'], 200)
        body = json.loads(response['body'])
        self.assertEqual(body, {"message": "API connection test successful"})

        # 验证日志记录
        mock_logger.info.assert_called_once()

    # 集成测试
    def test_api_integration(self):
        # 准备测试请求
        test_request = {
            "action": "test"
        }

        # 发送请求到 API Gateway
        response = self.api_client.test_invoke_method(
            restApiId=self.api_id,
            resourceId=self.get_resource_id(),
            httpMethod='POST',
            pathWithQueryString=self.resource_path,
            body=json.dumps(test_request)
        )

        # 验证响应
        self.assertEqual(response['status'], 200)
        body = json.loads(response['body'])
        self.assertEqual(body, {"message": "API connection test successful"})

    def get_resource_id(self):
        # 获取资源 ID
        resources = self.api_client.get_resources(restApiId=self.api_id)
        for item in resources['items']:
            if item.get('path') == self.resource_path:
                return item['id']
        raise ValueError(f"Resource {self.resource_path} not found")

if __name__ == '__main__':
    unittest.main()