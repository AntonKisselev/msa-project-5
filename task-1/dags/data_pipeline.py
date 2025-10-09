from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.dummy import DummyOperator
from airflow.operators.python import BranchPythonOperator
from airflow.utils.trigger_rule import TriggerRule
import pandas as pd
import os
import random

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2025,10,3),
    'retries': 2,
    'retry_delay': timedelta(minutes=1),
}

def send_email_mock(context, success=True):
    """Болванка для email уведомлений"""
    if success:
        print(f"EMAIL SUCCESS")
    else:
        print(f"EMAIL FAILED")

def create_sample_csv(**kwargs):
    """Создание CSV с 30 случайными числами от 0 до 100"""
    numbers = [random.randint(0, 100) for _ in range(30)]
    print(f"generated numbers: {numbers}")
    df = pd.DataFrame({'numbers': numbers})
    os.makedirs('/opt/airflow/data', exist_ok=True)
    csv_path = '/opt/airflow/data/numbers.csv'
    df.to_csv(csv_path, index=False)

    return csv_path

def read_csv_data(**kwargs):
    try:
        csv_path = '/opt/airflow/data/numbers.csv'

        if not os.path.exists(csv_path):
            csv_path = create_sample_csv()

        df = pd.read_csv(csv_path)

        if df.empty:
            raise ValueError("CSV file is empty")

        kwargs['ti'].xcom_push(key='numbers_data', value=df['numbers'].tolist())

        return f"Read {len(df)} numbers"

    except Exception as e:
        print(f"Failed to read CSV: {str(e)}")
        raise

def analyze_numbers(**kwargs):
    try:
        ti = kwargs['ti']

        numbers = ti.xcom_pull(task_ids='read_csv', key='numbers_data')

        # Вычисляем среднее значение
        average = sum(numbers) / len(numbers)

        print(f"   Numbers: {numbers}")
        print(f"   Average: {average:.2f}")

        # Простое условие ветвления
        if average > 50:
            print("анализ среднее больше 50")
            branch = 'average_high'
        else:
            print("анализ среднее меньше 50")
            branch = 'average_low'

        ti.xcom_push(key='average_value', value=average)

        return branch

    except Exception as e:
        print(f"Analysis failed: {str(e)}")
        raise

def process_high_average(**kwargs):
    ti = kwargs['ti']
    average = ti.xcom_pull(task_ids='analyze_data', key='average_value')

    print(f"Среднее больше 50: {average:.2f}")

    return "Среднее больше 50"

def process_low_average(**kwargs):
    ti = kwargs['ti']
    average = ti.xcom_pull(task_ids='analyze_data', key='average_value')

    print(f"Среднее меньше или равно 50: {average:.2f}")

    return "Среднее меньше или равно 50"

def final_summary(**kwargs):
    ti = kwargs['ti']
    branch = ti.xcom_pull(task_ids='analyze_data')
    average = ti.xcom_pull(task_ids='analyze_data', key='average_value')

    print(f"Результат: {branch}, Среднее: {average:.2f}")

    return f"Completed: {branch}"

# Callback функции
def success_callback(context):
    print("DAG completed successfully")
    send_email_mock(context, success=True)

def failure_callback(context):
    print("DAG failed")
    send_email_mock(context, success=False)

with DAG(
        'simple_numbers_pipeline',
        default_args=default_args,
        description='Simple numbers analysis with branching',
        schedule_interval=timedelta(minutes=30),
        catchup=False,
        tags=['numbers', 'simple'],
        on_success_callback=success_callback,
        on_failure_callback=failure_callback,
) as dag:

    start = DummyOperator(task_id='start')

    read_csv = PythonOperator(
        task_id='read_csv',
        python_callable=read_csv_data,
        retries=2,
        retry_delay=timedelta(minutes=1),
    )

    create_sample_csv = PythonOperator(
        task_id='create_csv',
        python_callable=create_sample_csv,
        retries=1,
    )

    analyze_data = BranchPythonOperator(
        task_id='analyze_data',
        python_callable=analyze_numbers,
        retries=2,
        retry_delay=timedelta(minutes=1),
    )

    high_avg_branch = PythonOperator(
        task_id='average_high',
        python_callable=process_high_average,
        retries=1,
    )

    low_avg_branch = PythonOperator(
        task_id='average_low',
        python_callable=process_low_average,
        retries=1,
    )

    final_task = PythonOperator(
        task_id='final_summary',
        python_callable=final_summary,
        retries=1,
        trigger_rule=TriggerRule.ONE_SUCCESS,
    )

    end = DummyOperator(task_id='end')

    # Workflow
    start >> create_sample_csv >> read_csv >> analyze_data
    analyze_data >> [high_avg_branch, low_avg_branch]
    [high_avg_branch, low_avg_branch] >> final_task >> end