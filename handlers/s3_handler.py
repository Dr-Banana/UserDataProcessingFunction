import boto3
import json
from botocore.exceptions import NoCredentialsError

s3_client = boto3.client('s3')

def download_json_from_s3(bucket_name, key):
    try:
        response = s3_client.get_object(Bucket=bucket_name, Key=key)
        print(response)
        json_data = json.loads(response['Body'].read())
        return json_data
    except Exception as e:
        print(f"Error downloading file from S3: {e}")
        return None

def save_to_s3(bucket_name, key, data):
    try:
        s3_client.put_object(Bucket=bucket_name, Key=key, Body=data)
        return True
    except Exception as e:
        print(f"Error saving data to S3: {e}")
        return False
