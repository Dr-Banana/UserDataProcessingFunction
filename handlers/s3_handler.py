# handlers/s3_handler.py

import boto3
import json

class S3Handler:
    def __init__(self):
        self.s3 = boto3.client('s3')

    def get_json_file(self, bucket, key):
        try:
            response = self.s3.get_object(Bucket=bucket, Key=key)
            data = response['Body'].read().decode('utf-8')
            return json.loads(data)
        except Exception as e:
            raise RuntimeError(f"Error getting object from S3: {str(e)}")
