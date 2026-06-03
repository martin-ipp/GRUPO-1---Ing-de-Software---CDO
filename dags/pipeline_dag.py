from airflow import DAG
from airflow.providers.standard.operators.python import PythonOperator
from datetime import datetime
import sys

sys.path.insert(0, "/usr/local/airflow")

from etl.setup_db import crear_tablas
from etl.extract import extract
from etl.transform import transform
from etl.aggregate import aggregate
from etl.load import load

with DAG(
    dag_id="pipeline_ventas",
    start_date=datetime(2024, 1, 1),
    schedule="@daily",
    catchup=False,
    description="Pipeline ETL de ventas: extract → transform → aggregate → load"
) as dag:

    tarea_crear_tablas = PythonOperator(
        task_id="crear_tablas",
        python_callable=crear_tablas
    )

    tarea_extract = PythonOperator(
        task_id="extract",
        python_callable=extract
    )

    tarea_transform = PythonOperator(
        task_id="transform",
        python_callable=transform
    )

    tarea_aggregate = PythonOperator(
        task_id="aggregate",
        python_callable=aggregate
    )

    tarea_load = PythonOperator(
        task_id="load",
        python_callable=load
    )

    tarea_crear_tablas >> tarea_extract >> tarea_transform >> tarea_aggregate >> tarea_load