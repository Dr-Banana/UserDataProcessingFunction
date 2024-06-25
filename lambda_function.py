import json
import logging
from config import PRESET_PROMPT, PARAMETERS, OUTPUT_BUCKET_NAME
from config.templates import get_input_data_json
from handlers.sagemaker_handler import call_sagemaker
from handlers.dynamodb_handler import save_to_dynamodb
from handlers.s3_handler import save_to_s3
from utils.json_processor import clean_and_check_json

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def lambda_handler(event, context):
    logger.info('Received event: %s', json.dumps(event))
    
    body = json.loads(event.get('body', '{}'))
    action = body.get('action', 'predict')
    input_text = body.get('input_text', '')
    user_id = body.get('UserID', '')
    
    if not input_text or not user_id:
        error_message = f'Invalid input: input_text={input_text}, UserID={user_id}'
        logger.error(error_message)
        return {
            'statusCode': 400,
            'body': json.dumps({'error': error_message})
        }

    if action == 'predict':
        try:
            # 调用 SageMaker 进行预测
            input_data_json = get_input_data_json(PRESET_PROMPT, input_text, PARAMETERS)
            result = call_sagemaker(input_data_json)
            logger.info('Raw SageMaker result: %s', result)

            # 清理和检查结果 JSON 数据
            cleaned_data, incomplete_entries = clean_and_check_json(result['body'])
            
            if cleaned_data is None:
                error_message = 'Failed to clean and check JSON data'
                logger.error(error_message)
                return {
                    'statusCode': 500,
                    'body': json.dumps({'error': error_message})
                }

            if incomplete_entries:
                logger.info('Incomplete Entries: %s', incomplete_entries)
                return {
                    'statusCode': 200,
                    'body': json.dumps({
                        'message': 'Incomplete entries found',
                        'incomplete_entries': incomplete_entries
                    })
                }

            # 将清理后的结果保存到 DynamoDB
            save_to_dynamodb(user_id, cleaned_data)
            logger.info('Saved cleaned result to DynamoDB for UserID: %s', user_id)
            
            # 将清理后的结果保存到 S3
            s3_key = f"{user_id}/result.json"
            save_to_s3(OUTPUT_BUCKET_NAME, s3_key, json.dumps(cleaned_data))
            logger.info('Saved cleaned result to S3: %s/%s', OUTPUT_BUCKET_NAME, s3_key)

            # 将 processed_content 保存到 S3
            processed_content_key = f"{user_id}/processed_content.json"
            save_to_s3(OUTPUT_BUCKET_NAME, processed_content_key, result['body'])
            logger.info('Saved processed content to S3: %s/%s', OUTPUT_BUCKET_NAME, processed_content_key)
            
            return {
                'statusCode': 200,
                'body': json.dumps(cleaned_data)
            }
        except Exception as e:
            logger.error('Error processing request: %s', str(e))
            return {
                'statusCode': 500,
                'body': json.dumps({'error': 'Error processing request', 'details': str(e)})
            }
    else:
        error_message = f'Invalid action: {action}'
        logger.error(error_message)
        return {
            'statusCode': 400,
            'body': json.dumps({'error': error_message})
        }
