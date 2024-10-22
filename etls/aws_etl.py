import boto3
from botocore.exceptions import ClientError

def connect_to_s3():
    try:
        s3_client = boto3.client('s3')
        print("Connected to AWS S3")
        return s3_client
    except Exception as e:
        print(f"Failed to connect to AWS S3: {e}")
        return None

def create_bucket_if_not_exist(s3, bucket):
    try:
        s3.create_bucket(Bucket=bucket)
        print("Bucket created")
    except ClientError as e:
        if e.response['Error']['Code'] == 'BucketAlreadyExists':
            print("Bucket already exists")
        else:
            print(e)

def upload_to_s3(s3, file_path, bucket, s3_file_name):
    try:
        s3.upload_file(file_path, f'raw/{s3_file_name}', bucket)
        print('File uploaded to S3')
    except FileNotFoundError:
        print('The file was not found')
    except ClientError as e:
        print(e)
