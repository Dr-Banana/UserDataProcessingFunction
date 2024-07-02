import boto3
import json
from utils.logger import setup_logger
from botocore.exceptions import NoCredentialsError

logger = setup_logger()
s3_client = boto3.client('s3')

def download_json_from_s3(bucket_name, key):
    try:
        logger.info(f"Downloading file from S3 bucket: {bucket_name}, key: {key}")
        response = s3_client.get_object(Bucket=bucket_name, Key=key)
        logger.debug(f"S3 response: {response}")
        json_data = json.loads(response['Body'].read())
        logger.info(f"Successfully downloaded file from S3: {key}")
        return json_data
    except boto3.exceptions.ClientError as e:
        error_code = e.response['Error']['Code']
        if error_code == 'NoSuchKey':
            logger.warning(f"File not found in S3: {key}")
            return None
        else:
            logger.error(f"Error downloading file from S3: {e}")
            raise RuntimeError(f"Error downloading file from S3: {e}")
    except json.JSONDecodeError as e:
        logger.error(f"Error decoding JSON data from S3: {e}")
        raise RuntimeError(f"Error decoding JSON data from S3: {e}")
    except Exception as e:
        logger.error(f"Unexpected error downloading file from S3: {e}")
        return None

def save_to_s3(bucket_name, key, data):
    try:
        s3_client.put_object(Bucket=bucket_name, Key=key, Body=data)
        return True
    except Exception as e:
        print(f"Error saving data to S3: {e}")
        return False
