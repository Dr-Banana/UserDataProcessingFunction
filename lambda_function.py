import json
from config.config import ENDPOINT_NAME, TABLE_NAME, PRESET_PROMPT, PARAMETERS, OUTPUT_BUCKET_NAME
from config.templates import get_input_data_json
from utils.logger import setup_logger
from handlers.s3_handler import save_to_s3
from handlers.sagemaker_handler import SageMakerHandler
from handlers.dynamodb_handler import DynamoDBHandler
from utils.json_processor import process_json

logger = setup_logger()

def lambda_handler(event, context):
    logger.info('Received event: %s', json.dumps(event))

    try:
        body = parse_event(event)
        action = body.get('action', 'predict')

        if action == 'predict':
            input_text = body.get('input_text', '')
            user_id = body.get('UserID', '')
            if not input_text or not user_id:
                return generate_response(400, {'error': f'Invalid input: input_text={input_text}, UserID={user_id}'})
            return handle_predict(input_text, user_id)
        elif action == 'test':
            return generate_response(200, {'message': 'API connection test successful'})
        else:
            return generate_response(400, {'error': f'Invalid action: {action}'})
    except Exception as e:
        logger.error('Error processing request: %s', str(e))
        return generate_response(500, {'error': 'Error processing request', 'details': str(e)})

def parse_event(event):
    return json.loads(event.get('body', '{}'))

def generate_response(status_code, body):
    return {
        'statusCode': status_code,
        'body': json.dumps(body)
    }

def handle_predict(input_text, user_id):
    try:
        processed_content = predict(input_text)
        save_result_to_s3(user_id, processed_content)
        save_result_to_dynamodb(user_id, processed_content)
        return generate_response(200, {'content': processed_content})
    except RuntimeError as e:
        logger.error(str(e))
        return generate_response(500, {'error': str(e)})

def predict(input_text):
    sagemaker_handler = SageMakerHandler(ENDPOINT_NAME)
    input_data_json = get_input_data_json(PRESET_PROMPT, input_text, PARAMETERS)
    
    try:
        result = sagemaker_handler.predict(input_data_json)
        logger.info('Raw SageMaker result: %s', result)  # 打印原始的 SageMaker 响应
        processed_content = process_json(result)
        return processed_content
    except Exception as e:
        logger.error(f"Error during prediction: {str(e)}")
        raise RuntimeError(f"Prediction failed: {str(e)}")

def save_result_to_s3(user_id, processed_content):
    s3_key = f"{user_id}/result.json"
    try:
        save_to_s3(OUTPUT_BUCKET_NAME, s3_key, json.dumps(processed_content))
        logger.info('Saved cleaned result to S3: %s/%s', OUTPUT_BUCKET_NAME, s3_key)
    except Exception as e:
        logger.error(f"Error saving to S3: {str(e)}")
        raise RuntimeError(f"Saving to S3 failed: {str(e)}")

def save_result_to_dynamodb(user_id, processed_content):
    dynamodb_handler = DynamoDBHandler(TABLE_NAME)
    try:
        dynamodb_handler.update_item(user_id, processed_content)
        logger.info('Saved result to DynamoDB for UserID: %s', user_id)
    except Exception as e:
        logger.error(f"Error saving to DynamoDB: {str(e)}")
        raise RuntimeError(f"Saving to DynamoDB failed: {str(e)}")