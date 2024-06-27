import unittest
import json
from lambda_function import lambda_handler

class TestLambdaFunction(unittest.TestCase):
    def test_lambda_handler(self):
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

if __name__ == '__main__':
    unittest.main()