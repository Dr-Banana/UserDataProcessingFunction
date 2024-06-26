import unittest
from unittest.mock import patch, MagicMock
import json
import lambda_function

class TestLambdaFunction(unittest.TestCase):

    @patch('lambda_function.save_to_s3')
    @patch('lambda_function.logger')
    @patch('lambda_function.SageMakerHandler.predict')
    @patch('lambda_function.DynamoDBHandler.update_item')
    def test_lambda_handler_success(self, mock_dynamodb_update, mock_sagemaker_predict, mock_logger, mock_save_to_s3):
        # 模拟 save_to_s3 方法
        mock_save_to_s3.return_value = None

        # 模拟 SageMaker predict 方法
        mock_sagemaker_predict.return_value = {
            'prediction': 'processed_result'
        }

        # 定义 event 和 context
        event = {
            "body": json.dumps({
                "action": "predict",
                "input_text": "I will have dinner with mom today afternoon at 7pm near downtown. Tomorrow morning at 9am, I have a meeting with the marketing team in the office. On Wednesday, there is a doctor's appointment at 3pm at the clinic.",
                "UserID": "1e026504-b625-4738-9e5d-e472c41510e4"
            })
        }
        context = {}

        # 调用 lambda handler
        response = lambda_function.lambda_handler(event, context)

        # 检查 save_to_s3 是否被正确调用
        mock_save_to_s3.assert_called_once_with(
            lambda_function.OUTPUT_BUCKET_NAME, 
            '1e026504-b625-4738-9e5d-e472c41510e4/result.json', 
            json.dumps('processed_result')
        )

        # 检查 logger.info 是否被正确调用
        mock_logger.info.assert_any_call(
            'Saved cleaned result to S3: %s/%s', 
            lambda_function.OUTPUT_BUCKET_NAME, 
            '1e026504-b625-4738-9e5d-e472c41510e4/result.json'
        )

        # 检查返回值
        self.assertEqual(response['statusCode'], 200)
        self.assertIn('content', json.loads(response['body']))

if __name__ == '__main__':
    unittest.main()
