from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime
import sys

sys.path.insert(0, "/usr/local/airflow")

from etl.transform import transform
from etl.aggregate import aggregate

with DAG(
    dag_id="pipeline_ventas",
    start_date=datetime(2024, 1, 1),
    schedule="@daily",
    catchup=False,
    description="Pipeline ETL de ventas: transform → aggregate"
) as dag:

    tarea_transform = PythonOperator(
        task_id="transform",
        python_callable=transform
    )

    tarea_aggregate = PythonOperator(
        task_id="aggregate",
        python_callable=aggregate
    )

    tarea_transform >> tarea_aggregate