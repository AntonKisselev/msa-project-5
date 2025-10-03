from datetime import datetime
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.dummy import DummyOperator

def simple_task():
    print("✅ Simple task executed successfully!")
    return "Success"

with DAG(
        'test_simple_dag',
        start_date=datetime(2025, 10, 3),
        schedule_interval=None,
        catchup=False,
        tags=['test'],
) as dag:

    start = DummyOperator(task_id='start')

    test_task = PythonOperator(
        task_id='test_task',
        python_callable=simple_task,
    )

    end = DummyOperator(task_id='end')

    start >> test_task >> end