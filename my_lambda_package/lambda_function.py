# lambda_function.py
import boto3
import pandas as pd
from io import StringIO
import json

def lambda_handler(event, context):
    
    s3=boto3.client('s3')

    bucket=event['s3_bucket']
    key=event['s3_key']

    response=s3.get_object(Bucket=bucket, Key=key)
    csv_content=response['Body'].read().decode('utf-8')

    df=pd.read_csv(StringIO(csv_content))

    #Calculate the avg price for each product
    result=df.groupby('product_type')['product_price'].mean().to_dict()
    result_csv= pd.DataFrame(list(result.items()), columns=['product_type','average_price'])

    result_buffer=StringIO()
    result_csv.to_csv(result_buffer, index=False)

    result_key=key.replace('product_data.csv', 'calculated_stats.csv')
    s3.put_object(Bucket=bucket, Key=result_key, Body=result_buffer.getvalue())

    return {
        'statusCode': 200,
        'body': json.dumps(f"Result saved to S3://{bucket}/{result_key}")
    }