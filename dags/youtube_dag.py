import os
import sys
from datetime import datetime

from airflow import DAG
from airflow.operators.python import PythonOperator

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pipelines.aws_pipeline import upload_s3_pipeline
from pipelines.youtube_pipeline import youtube_pipline

default_args = {
    'owner': 'An Nguyen',
    'start_date': datetime(2023, 10, 22)
}

file_postfix = datetime.now().strftime("%Y%m%d")

dag = DAG(
    dag_id='etl_youtube_pipeline',
    default_args=default_args,
    schedule='@daily',
    catchup=False,
    tags=['youtube', 'etl', 'pipeline']
)

extract = PythonOperator(
    task_id='youtube_extraction',
    python_callable=youtube_pipline,  # Reference the function without parentheses
    op_kwargs={
        'file_name': f'youtube_{file_postfix}',
        'db_table_name': 'youtubedata',
        'time_filter': 'day',
        'limit': 500
    },
    dag=dag
)

upload_s3 = PythonOperator(
    task_id='s3_upload',
    python_callable=upload_s3_pipeline,
    op_kwargs={},
    dag=dag
)

# Set the task dependencies
extract >> upload_s3