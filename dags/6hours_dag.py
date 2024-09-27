from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime,timedelta

# Define the Python functions that represent tasks
def task_1():
    print("The task is running for every 6 hours")


# Define the DAG and set its schedule
default_args = {
    'owner': 'airflow',
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

with DAG(   
    dag_id='6hours_dga',
    default_args=default_args,
    description='A simple example DAG which runs for every six hours',
    start_date=datetime(2023, 9, 23),
    schedule_interval=timedelta(hours=6),  # This DAG runs every six hours
    catchup=False,  # Disable backfilling of previous runs
) as dag:
    
    # Define Python tasks
    task_1 = PythonOperator(
        task_id='task_1',
        python_callable=task_1,
    )


    # Set the order of tasks
    task_1 