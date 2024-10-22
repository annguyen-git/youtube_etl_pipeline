FROM apache/airflow:2.10.2-python3.11

COPY requirements.txt /opt/airflow/

USER root
RUN apt-get update && \
    apt-get install -y gcc python3-dev pkg-config libmysqlclient-dev

USER airflow
RUN pip install --no-cache-dir -r /opt/airflow/requirements.txt
