#Youtube Data Pipeline

##Architecture
![alt text](https://github.com/annguyen-git/youtube_etl_pipeline/blob/main/Architecture.png)

- Youtube API: Source of the data.
- Apache Airflow: Schedules ETL tasks.
- MySQL: Storage and metadata management and transformed data.
- Amazon S3: Cloud storage.

Consider adding this:
- Amazon Redshift: For data analytics.
