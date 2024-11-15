# Youtube Data Pipeline

## Overview
This ETL pipeline extracts, transforms, and loads data from the YouTube API into a MySQL database and Amazon S3 storage. Using Apache Airflow, the pipeline automates data collection, transformation, and storage for efficient processing and retrieval, making it suitable for analysis and reporting purposes.

## Architecture
![alt text](https://github.com/annguyen-git/youtube_etl_pipeline/blob/main/Architecture.jpg)

- **YouTube API**: Data source for video metadata, statistics, and other channel information.
- **Apache Airflow**: Orchestrates and schedules ETL tasks.
- **MySQL**: Manages metadata and transformed data.
- **Amazon S3**: Stores processed data for easy access and backup.

Consider adding this:
- **Amazon Redshift**: For data analytics.

 ## ETL Flow
Airflow executes these tasks:
- Extraction: Pulls data from the YouTube API.
- Transformation: Cleans and processes the raw data into structured formats.
- Loading to MySQL: Stores transformed data into MySQL using SQLAlchemy.
- Backup to S3: Exports data from MySQL as CSV files and uploads them to an AWS S3 bucket for storage.
- (Optional) Loading to Redshift: For more extensive analytics, data can be loaded from S3 into Redshift.
The DAG execution completes successfully when data is backed up to S3.

## Prerequisites
- AWS free tier
- Youtube API credentials
- Docker
- Python 3.11 (Can be adjusted, check requirements.txt for compatibility)

## Usage
- Clone this repository and setup your virtual environment.
- Start the pipeline by enabling the DAG in Airflow.
- Monitor ETL stages in the Airflow UI, from extraction to loading.
- Access transformed data in MySQL or S3 for analysis.

## Future Enhancements
- Data Quality Checks: Add automated validation for incoming data.
- Error Handling and Logging: Improve resilience and traceability.
- Analytics with Redshift: Enable complex queries and visualization.
