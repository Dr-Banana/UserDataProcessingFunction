# handlers/s3_handler.py

import boto3
import json

s3 = boto3.client('s3')

def save_to_s3(bucket_name, key, content):
    try:
        s3.put_object(Bucket=bucket_name, Key=key, Body=json.dumps(content), ContentType='application/json')
        return True
    except Exception as e:
        print(f"Error saving to S3: {str(e)}")
        return False
