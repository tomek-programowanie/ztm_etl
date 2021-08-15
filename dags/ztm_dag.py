from datetime import timedelta
from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from airflow.utils.dates import days_ago
from ztm_etl import run_ztm_vehicles_etl

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': days_ago(1),
    'email': ['airflow@example.com'],
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 3,
    'retry_delay': timedelta(minutes=1)
}

dag = DAG(
    'ztm_dag',
    default_args=default_args,
    description='Downloading ztm data every hour',
    schedule_interval=timedelta(hours=1),
)

run_etl = PythonOperator(
    task_id='ztm_buses_trams',
    python_callable=run_ztm_vehicles_etl,
    dag=dag
)

run_etl