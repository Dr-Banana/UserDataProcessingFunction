import json
import unittest
from unittest.mock import patch
import boto3
import os
import logging
from botocore.exceptions import ClientError
from lambda_function import lambda_handler

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TestLambdaFunction(unittest.TestCase):

    def setUp(self):
        try:
            # 设置集成测试所需的 API Gateway 客户端
            self.api_client = boto3.client('apigateway', region_name='us-east-1')
            self.api_id = os.environ.get('API_GATEWAY_ID', '6inctbtbvk')
            self.stage_name = os.environ.get('API_STAGE_NAME', 'dev')
            self.resource_path = '/UserDataProcessingFunction'
            logger.info(f"Setup completed. API ID: {self.api_id}, Stage: {self.stage_name}")
        except Exception as e:
            logger.error(f"Error in setUp: {str(e)}")
            raise

    # 单元测试
    @patch('lambda_function.logger')
    def test_lambda_handler_unit(self, mock_logger):
        try:
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
            logger.info("Unit test passed successfully")
        except Exception as e:
            logger.error(f"Error in unit test: {str(e)}")
            raise

    # 集成测试
    def test_api_integration(self):
        try:
            # 准备测试请求
            test_request = {
                "action": "test"
            }

            logger.info(f"Attempting to get resource ID for path: {self.resource_path}")
            resource_id = self.get_resource_id()
            logger.info(f"Resource ID obtained: {resource_id}")

            logger.info("Sending request to API Gateway")
            # 发送请求到 API Gateway
            response = self.api_client.test_invoke_method(
                restApiId=self.api_id,
                resourceId=resource_id,
                httpMethod='POST',
                pathWithQueryString=self.resource_path,
                body=json.dumps(test_request)
            )

            logger.info(f"API Gateway response status: {response['status']}")
            logger.info(f"API Gateway response body: {response['body']}")

            # 验证响应
            self.assertEqual(response['status'], 200)
            body = json.loads(response['body'])
            self.assertEqual(body, {"message": "API connection test successful"})
            logger.info("Integration test passed successfully")
        except ClientError as e:
            logger.error(f"AWS API error: {e.response['Error']['Message']}")
            raise
        except Exception as e:
            logger.error(f"Error in integration test: {str(e)}")
            raise

    def get_resource_id(self):
        try:
            # 获取资源 ID
            logger.info(f"Getting resources for API ID: {self.api_id}")
            resources = self.api_client.get_resources(restApiId=self.api_id)
            logger.info(f"Resources retrieved: {resources}")
            for item in resources['items']:
                if item.get('path') == self.resource_path:
                    logger.info(f"Resource ID found: {item['id']}")
                    return item['id']
            raise ValueError(f"Resource {self.resource_path} not found")
        except ClientError as e:
            logger.error(f"AWS API error in get_resource_id: {e.response['Error']['Message']}")
            raise
        except Exception as e:
            logger.error(f"Error in get_resource_id: {str(e)}")
            raise

if __name__ == '__main__':
    unittest.main()