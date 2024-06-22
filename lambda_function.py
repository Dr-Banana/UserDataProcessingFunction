# lambda_function.py

import json
from config.config import ENDPOINT_NAME, TABLE_NAME, PRESET_PROMPT, PARAMETERS
from config.templates import get_input_data_json
from utils.logger import setup_logger
from handlers.sagemaker_handler import SageMakerHandler
from handlers.dynamodb_handler import DynamoDBHandler
from utils.json_processor import process_json

logger = setup_logger()

def lambda_handler(event, context):
    logger.info('Received event: %s', json.dumps(event))

    try:
        body = json.loads(event.get('body', '{}'))
        action = body.get('action', 'predict')
        input_text = body.get('input_text', '')
        user_id = body.get('UserID', '')
        dialog_state = body.get('dialog_state', None)

        if not input_text or not user_id:
            error_message = f'Invalid input: input_text={input_text}, UserID={user_id}'
            logger.error(error_message)
            return {
                'statusCode': 400,
                'body': json.dumps({'error': error_message})
            }

        if action == 'predict':
            sagemaker_handler = SageMakerHandler(ENDPOINT_NAME)
            dynamodb_handler = DynamoDBHandler(TABLE_NAME)

            # 构建发送给SageMaker端点的请求体
            input_data_json = get_input_data_json(PRESET_PROMPT, input_text, PARAMETERS)
            
            try:
                result = sagemaker_handler.predict(input_data_json)
                logger.info('Raw SageMaker result: %s', result)  # 打印原始的 SageMaker 响应
                processed_content = process_json(result)
            except RuntimeError as e:
                logger.error(str(e))
                return {
                    'statusCode': 500,
                    'body': json.dumps({'error': str(e)})
                }

            # 检查是否有跟进问题
            if "follow_up_question" in processed_content:
                return {
                    'statusCode': 200,
                    'body': json.dumps({
                        'follow_up_question': processed_content['follow_up_question'],
                        'dialog_state': dialog_state  # 返回当前对话状态
                    })
                }

            # 将结果保存到DynamoDB
            try:
                dynamodb_handler.update_item(user_id, processed_content)
                logger.info('Saved result to DynamoDB for UserID: %s', user_id)
            except RuntimeError as e:
                logger.error(str(e))
                return {
                    'statusCode': 500,
                    'body': json.dumps({'error': str(e)})
                }

            return {
                'statusCode': 200,
                'body': json.dumps({'result content': processed_content})
            }
        else:
            error_message = f'Invalid action: {action}'
            logger.error(error_message)
            return {
                'statusCode': 400,
                'body': json.dumps({'error': error_message})
            }
    except Exception as e:
        logger.error('Error processing request: %s', str(e))
        return {
            'statusCode': 500,
            'body': json.dumps({'error': 'Error processing request', 'details': str(e)})
        }
