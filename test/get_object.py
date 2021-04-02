import boto3
import os

client = boto3.client('s3')
sts = boto3.client('sts')

caller_identity = sts.get_caller_identity()
account = caller_identity['Account']

BUCKET_NAME = os.environ.get('BUCKET_NAME')
LAMBDA_ACCESSPOINT_NAME = os.environ.get('LAMBDA_ACCESSPOINT_NAME')
LAMBDA_ACCESSPINT = 'arn:aws:s3-object-lambda:ap-northeast-1:{}:accesspoint/{}'.format(account, LAMBDA_ACCESSPOINT_NAME)
KEY_NAME = 'index.txt'

response = client.get_object(
    Bucket=BUCKET_NAME,
    Key=KEY_NAME,
)

print(response['Body'].read().decode('utf8'))

response = client.get_object(
    Bucket=LAMBDA_ACCESSPINT,
    Key=KEY_NAME + '@202102',
)

print(response['Body'].read().decode('utf8'))

response = client.get_object(
    Bucket=LAMBDA_ACCESSPINT,
    Key=KEY_NAME + '@latest',
)

print(response['Body'].read().decode('utf8'))

response = client.get_object(
    Bucket=LAMBDA_ACCESSPINT,
    Key=KEY_NAME + '@earliest',
)

print(response['Body'].read().decode('utf8'))

response = client.get_object(
    Bucket=LAMBDA_ACCESSPINT,
    Key=KEY_NAME + '@1990',
)

print(response['Body'].read().decode('utf8'))

response = client.get_object(
    Bucket=LAMBDA_ACCESSPINT,
    Key=KEY_NAME + '@log',
)

print(response['Body'].read().decode('utf8'))
