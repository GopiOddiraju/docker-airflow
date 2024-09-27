from airflow import DAG
from airflow.providers.amazon.aws.operators.s3 import S3ListOperator
from datetime import datetime

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'retries': 0,
}

with DAG(
    dag_id='localstack_s3_dag',
    default_args=default_args,
    description='A simple DAG to interact with LocalStack S3',
    schedule_interval=None,
    start_date=datetime(2023, 9, 22),
    catchup=False,
) as dag:

    list_s3_buckets = S3ListOperator(
        task_id='list_s3_buckets',
        aws_conn_id='localstack_s3',  # Connection to LocalStack S3
        bucket='test',  # List all buckets
    )

    list_s3_buckets
