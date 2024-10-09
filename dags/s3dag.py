from airflow import DAG
from airflow.providers.amazon.aws.operators.s3 import S3ListOperator
from airflow.operators.python_operator import PythonOperator
from datetime import datetime, timedelta
import pandas as pd
import random
from io import StringIO
import boto3
from airflow.hooks.base_hook import BaseHook

S3_BUCKET_NAME = "test"
now=datetime.now()
year=now.strftime("%Y")
month=now.strftime("%m")
day=now.strftime("%d")


def upload_csv_to_s3(**kwargs):

    aws_conn = BaseHook.get_connection('localstack_s3')
    data = {
        'product_id' : [random.randint(1,100) for i in range(10)],
        'product_type' : [random.choice(['Electronics', 'Clothing', 'Furniture', 'Food', 'Alcohol']) for i in range(10)],
        'product_price' : [random.uniform(1.0,100.0) for i in range(10)],
        'ordered_date' : [(datetime.now() - timedelta(days=random.randint(0,30))).strftime('%Y-%m-%d %H:%M:%S') for i in range(10)]
    }

    df=pd.DataFrame(data)

    csv_buffer=StringIO()
    df.to_csv(csv_buffer, index=False)

    s3_key = f"{year}{month}{day}product_data.csv" year=2024/month=10/day=01

    s3_client = boto3.client('s3',endpoint_url='http://localstack:4566', aws_access_key_id=aws_conn.login, aws_secret_access_key=aws_conn.password)

    s3_client.put_object(Bucket=S3_BUCKET_NAME, Key=s3_key, Body=csv_buffer.getvalue())

    print(f"Uploaded CSV to S3://{S3_BUCKET_NAME}/{s3_key}")


default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'retries': 1,
}

with DAG(
    dag_id='localstack_s3_dag',
    default_args=default_args,
    description='A simple DAG to interact with LocalStack S3',
    start_date=datetime(2024, 9, 29),
    schedule_interval='@daily',
    catchup=False,
) as dag:

    list_s3_buckets = S3ListOperator(
        task_id='list_s3_buckets',
        aws_conn_id='localstack_s3',  # Connection to LocalStack S3
        bucket=S3_BUCKET_NAME,  # List all buckets
    )

    upload_csv_to_s3 = PythonOperator(
        task_id='upload_csv_to_s3',
        python_callable=upload_csv_to_s3,
        provide_context=True,
    )

    list_s3_buckets >> upload_csv_to_s3
