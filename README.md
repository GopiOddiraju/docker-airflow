# AWS Lambda Deployment with Airflow Automation (Using LocalStack)


## Overview
This project demonstrates how to deploy an AWS Lambda function that uses external dependencies (like pandas, numpy, etc.) and automate its executionusing Apache Airflow. The setup includesusing LocalStack to simulate AWS services (Lambda, S3, etc.) locally along with Docker to run Airflow, creating a robust local development environment.


## Prerequisites
Before starting, ensure you have the following:

- Docker installed and running (for Airflow and LocalStack)
- Python 3.x installed
- AWS CLI installed and configured (use the --endpoint-URL to interact with LocalStack)


## Step-by-Step Guide


### Step 1: Setting Up Apache Airflow with Docker

We'll set up Airflow to automate the invocation of an AWS Lambda function. Docker will be used to run Airflow services (webserver, scheduler) along with LocalStack, which will simulate AWS services locally.

1. Install Docker Desktop (If not installed already) from [Docker's website](https://www.docker.com/).
2. Modify the [docker-compose.yaml](https://github.com/GopiOddiraju/docker-airflow/blob/feature/docker-airflow/docker-compose.yaml) file to include LocalStack along with Airflow.
3. Start the Airflow and LocalStack services using Docker Compose.

   ```
   docker-compose up -d
   ```
4. Access the AIrflow UI at http:localhost:8080. Create a user to access the Airflow UI.

   ```
   docker exec -it <airflow-webserver-container-name> airflow users create \
    --username admin \
    --password admin \
    --firstname John \
    --lastname Doe \
    --role Admin \
   ```
   This will allow you to log in to the Airflow UI using the "admin" username and password.



### Step 2: Set Up Connection Between Airflow and LocalStack

In the Airflow UI:
- Navigate to Admin > Connections.
- Create a new connection:
    - Connetion ID : localstack_s3
    - Connection Type : Amazon Web Services
    - Extra : {"region_name":"us-east-1", "endpoint_url":"http://localstack:4566"}

 This establishes the connection between Airflow and the AWS services simulated by LocalStack.



### Step 3: DAG Creation

The main workflow for this project is handled by an Airflow Directed Acyclic Graph (DAG). This DAG orchestrates the entire process of interacting with S3, deploying the Lambda function, and processing data.

### DAG Tasks Overview

The DAG (docker-airfow/dags/lambda.py) consists of three key tasks:

#### List S3 Buckets
This task uses a S3ListOperator to list the existing S3 buckets within LocalStack. It ensures that the required buckets are in place before performing other operations.

#### Upload CSV to S3
This task dynamically creates a sample CSV file (using Python and Pandas) and uploads it to an S3 bucket in LocalStack. It simulates data being ingested into the system for processing.

#### Invoke Lambda to Process S3 Data
This task triggers the AWS Lambda function that reads the CSV data from S3, processes it (e.g., applying transformations using Pandas), and writes the results back to another S3 bucket.



### Step 4: Writing the Lambda Function

Now, we'll write the actual Lambda function (docker-airflow/my_lambda_package/lambda_function.py) that gets invoked by Airfow via LocalStack.



### Step 5: Installing Dependencies for Lambda

AWS Lambda requires bundling external dependencies with your code. We’ll use LocalStack to simulate Lambda deployment.

1. Install the necessary packages in a local folder (my_lambda_package):
```
pip install pandas numpy pytz python-dateutil six --target ./lambda/my_lambda_package
```

2. Zip the Package

```
Compress-Archive -Path * -DestinationPath my_deployment_package.zip
```



### Step 6: Deploying Lambda to LocalStack

With LocalStack running, we'll now deploy the Lambda function to LocalStack.

1. Use the AWS CLI (configured to point to LocalStack) to create the Lambda function.

```
aws --endpoint-url=http://localhost:4566 lambda create-function \
--function-name lambda_function \
--runtime python3.8 \
--role arn:aws:iam::000000000000:role/dummy \
--handler lambda_function.lambda_handler \
--zip-file fileb://my_deployment_package.zip
```

2. Test the lambda function in LocalStack:

```
aws --endpoint-url=http://localhost:4566 lambda invoke \
--function-name lambda_function response.json
```



### Step 7: Automating Lambda Invocation with Airflow

Now that the connection is set and the Lambda function is deployed, the DAG will be able to trigger Lambda functions on LocalStack automatically, based on the schedule we set in the DAG.




### Technologies Used
- Apache Airflow: For orchestrating and automating workflows.
- Docker: For containerizing Airflow and LocalStack services.
- LocalStack: A fully functional local AWS cloud stack, simulating AWS services like S3, Lambda.
- AWS CLI: For interacting with LocalStack's simulated AWS services.
- Python: Used to write the Airflow DAGs and the AWS Lambda function.
- Boto3: Python SDK to interact with AWS services.
- Pandas: Used for data manipulation and CSV generation in the DAG.
- AWS S3: Simulated by LocalStack, used for data storage.
- AWS Lambda: Simulated by LocalStack, used for processing data.
- PostgreSQL: Airflow's metadata database, running in a Docker container.


