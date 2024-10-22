from etls.aws_etl import connect_to_s3, create_bucket_if_not_exist, upload_to_s3
from utils.constants import AWS_BUCKET_NAME

def upload_s3_pipeline(ti):
    file_path = ti.xcom_pull(task_ids='reddit_extraction', key='return_value')

    # Connect to S3
    s3 = connect_to_s3()
    if s3 is None:
        raise Exception("Failed to connect to AWS S3")

    # Create bucket if it does not exist
    create_bucket_if_not_exist(s3, AWS_BUCKET_NAME)

    # Upload the file to S3
    upload_to_s3(s3, file_path, AWS_BUCKET_NAME, file_path.split('/')[-1])
    print(f"Uploaded {file_path} to {AWS_BUCKET_NAME}/raw/")
