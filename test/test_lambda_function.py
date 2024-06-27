import json
import unittest
from unittest.mock import patch, MagicMock
import boto3
import os
import logging
from botocore.exceptions import ClientError

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TestLambdaFunction(unittest.TestCase):

    def setUp(self):
        try:
            self.api_client = boto3.client('apigateway', region_name='us-east-1')
            self.api_id = '6inctbtbvk'  # 直接使用正确的 API ID
            self.stage_name = 'dev'
            self.resource_path = '/UserDataProcessingFunction'
            logger.info(f"Setup completed. API ID: {self.api_id}, Stage: {self.stage_name}")
        except Exception as e:
            logger.error(f"Error in setUp: {str(e)}")
            raise

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
            logger.error(f"Full error response: {json.dumps(e.response, default=str)}")
            raise
        except Exception as e:
            logger.error(f"Error in integration test: {str(e)}")
            raise

    def get_resource_id(self):
        try:
            logger.info(f"Getting resources for API ID: {self.api_id}")
            resources = self.api_client.get_resources(restApiId=self.api_id)
            logger.info(f"Resources retrieved: {json.dumps(resources, default=str)}")
            for item in resources['items']:
                logger.info(f"Checking resource: {item}")
                if item.get('path') == self.resource_path:
                    logger.info(f"Resource ID found: {item['id']}")
                    return item['id']
            raise ValueError(f"Resource {self.resource_path} not found")
        except ClientError as e:
            logger.error(f"AWS API error in get_resource_id: {e.response['Error']['Message']}")
            logger.error(f"Full error response: {json.dumps(e.response, default=str)}")
            raise
        except Exception as e:
            logger.error(f"Error in get_resource_id: {str(e)}")
            raise

if __name__ == '__main__':
    unittest.main()