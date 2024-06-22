# handlers/sagemaker_handler.py

import boto3
import json

class SageMakerHandler:
    def __init__(self, endpoint_name):
        self.runtime = boto3.client('runtime.sagemaker')
        self.endpoint_name = endpoint_name

    def predict(self, input_data):
        try:
            payload = json.dumps(input_data)
            response = self.runtime.invoke_endpoint(
                EndpointName=self.endpoint_name,
                ContentType='application/json',
                Body=payload,
                CustomAttributes='accept_eula=true'
            )
            response_content = response['Body'].read().decode('utf-8')
            return json.loads(response_content)
        except Exception as e:
            raise RuntimeError(f"Error calling SageMaker endpoint: {str(e)}")
