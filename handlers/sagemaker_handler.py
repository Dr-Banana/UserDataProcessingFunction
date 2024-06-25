import boto3
import json

runtime = boto3.client('runtime.sagemaker')
from config import ENDPOINT_NAME

def call_sagemaker(input_data_json):
    response = runtime.invoke_endpoint(
        EndpointName=ENDPOINT_NAME,
        ContentType='application/json',
        Body=json.dumps(input_data_json),
        CustomAttributes='accept_eula=true'
    )
    response_content = response['Body'].read().decode('utf-8')
    return json.loads(response_content)
