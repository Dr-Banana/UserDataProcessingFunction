import json
import logging
from config import PRESET_PROMPT, PARAMETERS
from handlers.sagemaker_handler import call_sagemaker
from handlers.dynamodb_handler import save_to_dynamodb

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
            # 调用SageMaker进行预测
            input_data_json = {
                "inputs": [
                    [
                        {"role": "system", "content": PRESET_PROMPT},
                        {"role": "user", "content": input_text}
                    ]
                ],
                "parameters": PARAMETERS
            }
            
            result = call_sagemaker(input_data_json)
            logger.info('Raw SageMaker result: %s', result)

            # 检查结果是否需要进一步提问
            if 'needs_confirmation' in result:
                return {
                    'statusCode': 200,
                    'body': json.dumps(result)
                }

            # 将结果保存到DynamoDB
            save_to_dynamodb(user_id, result)
            logger.info('Saved result to DynamoDB for UserID: %s', user_id)
            
            return {
                'statusCode': 200,
                'body': json.dumps(result)
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
