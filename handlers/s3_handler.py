from botocore.exceptions import NoCredentialsError

def download_json_from_s3(s3_client, bucket_name, file_name):
    try:
        response = s3_client.get_object(Bucket=bucket_name, Key=file_name)
        json_data = response['Body'].read().decode('utf-8')
        return json_data
    except Exception as e:
        print(f"Error downloading file from S3: {e}")
        return None

def upload_json_to_s3(s3_client, bucket_name, file_name, json_data):
    try:
        s3_client.put_object(Bucket=bucket_name, Key=file_name, Body=json_data)
        return True
    except NoCredentialsError:
        print("Credentials not available")
        return False
    except Exception as e:
        print(f"Error uploading file to S3: {e}")
        return False

def save_to_s3(s3_client, bucket_name, key, data):
    try:
        s3_client.put_object(Bucket=bucket_name, Key=key, Body=data)
        return True
    except Exception as e:
        print(f"Error saving data to S3: {e}")
        return False
