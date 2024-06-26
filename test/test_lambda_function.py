import unittest
from unittest.mock import patch
import lambda_function

class TestLambdaFunction(unittest.TestCase):

    @patch('lambda_function.save_to_s3')
    @patch('lambda_function.logger')
    def test_lambda_handler_success(self, mock_logger, mock_save_to_s3):
        # 模拟 save_to_s3 方法
        mock_save_to_s3.return_value = None

        # 定义 event 和 context
        event = {
            # 在这里定义你的 event 数据
        }
        context = {}

        # 调用 lambda handler
        lambda_function.handler(event, context)

        # 检查 save_to_s3 是否被正确调用
        mock_save_to_s3.assert_called_once_with(
            'your_output_bucket_name', 'your_s3_key', 'json.dumps(processed_content)'
        )

        # 检查 logger.info 是否被正确调用
        mock_logger.info.assert_called_with(
            'Saved cleaned result to S3: %s/%s', 'your_output_bucket_name', 'your_s3_key'
        )

if __name__ == '__main__':
    unittest.main()
