import json
import unittest
import requests
import os

API_URL = os.environ.get('API_URL', 'https://6inctbtbvk.execute-api.us-east-1.amazonaws.com/dev/UserDataProcessingFunction')

class TestLambdaFunction(unittest.TestCase):

    def test_api_connection(self):
        """测试 API 连接"""
        payload = {
            "action": "test"
        }
        headers = {
            'Content-Type': 'application/json'
        }

        response = requests.post(API_URL, json=payload, headers=headers)

        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertEqual(body, {"message": "API connection test successful"})

    def test_predict_action(self):
        """测试 predict 动作"""
        payload = {
            "action": "predict",
            "input_text": "测试输入文本",
            "UserID": "test-user-id"
        }
        headers = {
            'Content-Type': 'application/json'
        }

        response = requests.post(API_URL, json=payload, headers=headers)

        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertIn('content', body)
        # 这里可以添加更多具体的断言来验证返回的内容

    def test_invalid_action(self):
        """测试无效的 action"""
        payload = {
            "action": "invalid_action"
        }
        headers = {
            'Content-Type': 'application/json'
        }

        response = requests.post(API_URL, json=payload, headers=headers)

        self.assertEqual(response.status_code, 400)
        body = response.json()
        self.assertIn('error', body)
        self.assertIn('Invalid action', body['error'])

if __name__ == '__main__':
    unittest.main()