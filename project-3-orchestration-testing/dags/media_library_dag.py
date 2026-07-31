from datetime import datetime
from airflow import DAG
from airflow.operators.bash import BashOperator

PROJECT_DIR = "/opt/airflow/project-1-media-library-pipeline"
DBT_DIR = f"{PROJECT_DIR}/media_library"

with DAG(
    dag_id="media_library_pipeline",
    description="Extract Navidrome + Jellyfin library data + Sonarr/Radarr activity, load to Postgres, run dbt",
    start_date=datetime(2026, 7, 30),
    schedule="@daily",
    catchup=False,
    tags=["project-1", "project-2", "media-library"],
) as dag:

    extract_navidrome = BashOperator(
        task_id="extract_navidrome",
        bash_command=f"cd {PROJECT_DIR} && python3 extract_navidrome.py",
    )

    load_navidrome = BashOperator(
        task_id="load_navidrome",
        bash_command=f"cd {PROJECT_DIR} && python3 load_to_postgres.py",
    )

    extract_jellyfin = BashOperator(
        task_id="extract_jellyfin",
        bash_command=f"cd {PROJECT_DIR} && python3 extract_jellyfin.py",
    )

    load_jellyfin = BashOperator(
        task_id="load_jellyfin",
        bash_command=f"cd {PROJECT_DIR} && python3 load_jellyfin_to_postgres.py",
    )

    extract_sonarr = BashOperator(
        task_id="extract_sonarr",
        bash_command=f"cd {PROJECT_DIR} && python3 extract_sonarr.py",
    )

    load_sonarr = BashOperator(
        task_id="load_sonarr",
        bash_command=f"cd {PROJECT_DIR} && python3 load_sonarr_to_postgres.py",
    )

    extract_radarr = BashOperator(
        task_id="extract_radarr",
        bash_command=f"cd {PROJECT_DIR} && python3 extract_radarr.py",
    )

    load_radarr = BashOperator(
        task_id="load_radarr",
        bash_command=f"cd {PROJECT_DIR} && python3 load_radarr_to_postgres.py",
    )

    dbt_run = BashOperator(
        task_id="dbt_run",
        bash_command=f"cd {DBT_DIR} && dbt run",
    )

    extract_navidrome >> load_navidrome >> extract_jellyfin >> load_jellyfin >> extract_sonarr >> load_sonarr >> extract_radarr >> load_radarr >> dbt_run
