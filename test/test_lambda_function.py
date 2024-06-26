import unittest
from unittest.mock import patch, MagicMock
import json
import lambda_function
import requests

class TestLambdaFunction(unittest.TestCase):

    @patch('requests.post')
    @patch('lambda_function.save_to_s3')
    @patch('lambda_function.logger')
    def test_lambda_handler_success(self, mock_logger, mock_save_to_s3, mock_post):
        # 模拟 save_to_s3 方法
        mock_save_to_s3.return_value = None

        # 模拟 Postman API 调用
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"message": "success"}
        mock_post.return_value = mock_response

        # 定义 event 和 context
        event = {
            # 在这里定义你的 event 数据
        }
        context = {}

        # 调用 lambda handler
        lambda_function.handler(event, context)

        # 检查 Postman API 是否被正确调用
        mock_post.assert_called_once_with(
            'https://95zkfcumvb.execute-api.us-east-1.amazonaws.com/default/UserDataProcessingFunction',
            headers={'Content-Type': 'application/json'},
            data=json.dumps({
                "action": "predict",
                "input_text": "I will have dinner with mom today afternoon at 7pm near downtown. Tomorrow morning at 9am, I have a meeting with the marketing team in the office. On Wednesday, there is a doctor's appointment at 3pm at the clinic.",
                "UserID": "1e026504-b625-4738-9e5d-e472c41510e4"
            })
        )

if __name__ == '__main__':
    unittest.main()
