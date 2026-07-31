FROM apache/airflow:2.9.2

USER root
RUN apt-get update && apt-get install -y --no-install-recommends libpq-dev gcc libc6-dev && rm -rf /var/lib/apt/lists/*
USER airflow

RUN pip install --no-cache-dir dbt-postgres==1.8.0 "dbt-core==1.8.0"
