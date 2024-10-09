from airflow import DAG
from airflow.providers.amazon.aws.hooks.lambda_function import LambdaHook
from airflow.providers.amazon.aws.operators.s3 import S3ListOperator
from airflow.operators.python_operator import PythonOperator
from datetime import datetime, timedelta
import pandas as pd
import random
from io import StringIO
import boto3
from airflow.hooks.base_hook import BaseHook
import json


S3_BUCKET_NAME = "test"
now=datetime.now()
year=now.strftime("%Y")
month=now.strftime("%m")
day=now.strftime("%d")


def upload_csv_to_s3(**kwargs):

    aws_conn = BaseHook.get_connection('localstack_s3')
    
    data = {
        'product_id' : [random.randint(1,100) for i in range(100)],
        'product_type' : [random.choice(['Electronics', 'Clothing', 'Furniture', 'Food', 'Alcohol']) for i in range(100)],
        'product_price' : [random.uniform(1.0,100.0) for i in range(100)],
        'ordered_date' : [(datetime.now() - timedelta(days=random.randint(0,30))).strftime('%Y-%m-%d %H:%M:%S') for i in range(100)]
    }

    df=pd.DataFrame(data)

    csv_buffer=StringIO()
    df.to_csv(csv_buffer, index=False)

    s3_key = f"{year}/{month}/{day}/product_data.csv" 

    s3_client = boto3.client('s3',endpoint_url='http://localstack:4566', aws_access_key_id=aws_conn.login, aws_secret_access_key=aws_conn.password)

    s3_client.put_object(Bucket=S3_BUCKET_NAME, Key=s3_key, Body=csv_buffer.getvalue())

    print(f"Uploaded CSV to S3://{S3_BUCKET_NAME}/{s3_key}")
    return s3_key



def invoke_lambda_function(**kwargs):
    
    s3_key = kwargs['task_instance'].xcom_pull(task_ids='upload_csv_to_s3')
    
    hook= LambdaHook(aws_conn_id='localstack_s3'
                     )
    payload = json.dumps({"s3_bucket": S3_BUCKET_NAME, "s3_key": s3_key})
    
    # Invoke the Lambda function
    response = hook.invoke_lambda(payload=payload, invocation_type="RequestResponse", function_name='lambda_function')

    # The response will be a dictionary, access 'Payload' to get the StreamingBody
    response_payload = response['Payload'].read()  # Reading the StreamingBody
    response_json = json.loads(response_payload)  # Convert the StreamingBody content to JSON
    
    print(f"Lambda response: {response_json}")
    return response_json

default_args = {
    'owner': 'airflow',
    'start_date': datetime(2023, 10,3),
    'retries': 0,
}

with DAG(dag_id='localstack_s3_dag_with_lambda',
         default_args=default_args,
         description='A DAG that uploads data to S3, processes it using Lambda, and stores the result back in S3',
         schedule_interval='@daily',
         catchup=False) as dag:

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


    invoke_lambda_task = PythonOperator(
        task_id='invoke_lambda',
        python_callable=invoke_lambda_function,
        provide_context=True,
    )

    list_s3_buckets >> upload_csv_to_s3 >> invoke_lambda_task
