import boto3
import json
import logging
from config import ENDPOINT_NAME

logger = logging.getLogger()
logger.setLevel(logging.INFO)

runtime = boto3.client('runtime.sagemaker')

def call_sagemaker(input_data_json):
    response = runtime.invoke_endpoint(
        EndpointName=ENDPOINT_NAME,
        ContentType='application/json',
        Body=json.dumps(input_data_json),
        CustomAttributes='accept_eula=true'
    )

    response_content = response['Body'].read().decode('utf-8')
    result = json.loads(response_content)
    
    # 检查是否需要提问
    if 'incomplete' in result:
        return {
            'needs_confirmation': True,
            'question': result['incomplete']['question']
        }

    return result
