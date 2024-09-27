from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime,timedelta
from airflow.exceptions import AirflowSkipException

# Define the Python functions that represent tasks
def task_1():
    print("Task 1 is running!")

def task_2():
    print("Task 2 is running!")

def task_3():
    raise AirflowSkipException('Skipping the task for fun')

def task_4():
    print("Task 4 is running")

# Define the DAG and set its schedule
default_args = {
    'owner': 'airflow',
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

with DAG(
    dag_id='example_dag',
    default_args=default_args,
    description='A simple example DAG',
    start_date=datetime(2023, 9, 22),
    schedule_interval='@daily',  # This DAG runs once daily
    catchup=False,  # Disable backfilling of previous runs
) as dag:
    
    # Define Python tasks
    task_1 = PythonOperator(
        task_id='task_1',
        python_callable=task_1,
    )
    
    task_2 = PythonOperator(
        task_id='task_2',
        python_callable=task_2,
    )

    task_3 = PythonOperator(
        task_id='task_3',
        python_callable=task_3,
    )

    task_4 = PythonOperator(
        task_id='task_4',
        python_callable=task_4,
    )

    # Set the order of tasks
    task_1 >> task_2  # task_1 runs first, followed by task_2
    task_1 >> task_3 >> task_4 
    #task_1 >> [task_2, task_3 >> task_4]