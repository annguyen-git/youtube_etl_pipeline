# Youtube Data Pipeline

## Architecture
![alt text](https://github.com/annguyen-git/youtube_etl_pipeline/blob/main/Architecture.png)

- Youtube API: Source of the data.
- Apache Airflow: Schedules ETL tasks.
- MySQL: Storage and metadata management and transformed data.
- Amazon S3: Cloud storage.

Consider adding this:
- Amazon Redshift: For data analytics.

 ## ETL Flow
Airflow schedules and perform these tasks:
- Data collected from the Youtube API is transformed to ready to use data.
- Transformed data then loaded into MySQL database using alchemysql.
- Once completed loading into database, data is push to cloud service - AWS S3 bucket as csv file.
- DAG executions finish after data is successfully uploaded to S3.

## Prerequisites
- AWS free tier
- Youtube API credentials
- Docker
- Python 3.11 (Can be adjusted, check requirements.txt for compatibility)
