import boto3
import json
from botocore.exceptions import ClientError

s3 = boto3.client('s3')
BUCKET_NAME = 'your-s3-bucket-name'

def upload_to_s3(data, key):
    try:
        s3.put_object(Bucket=BUCKET_NAME, Key=key, Body=data)
    except ClientError as e:
        raise Exception(f'Error uploading to S3: {str(e)}')

def download_from_s3(key):
    try:
        response = s3.get_object(Bucket=BUCKET_NAME, Key=key)
        return response['Body'].read().decode('utf-8')
    except ClientError as e:
        raise Exception(f'Error downloading from S3: {str(e)}')
