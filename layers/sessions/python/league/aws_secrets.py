import os

import boto3

INVITE_SECRET: str

secret_name = os.getenv('INVITE_KEY')
aws_region = os.getenv('REGION')

if secret_name is None:
    raise RuntimeError('Environment variable INVITE_KEY is not set.')

if aws_region is None:
    raise RuntimeError('Environment variable AWS_REGION is not set.')

sm_client = boto3.client(service_name='secretsmanager', region_name=aws_region)

secret_response = sm_client.get_secret_value(SecretId=secret_name)

INVITE_SECRET = secret_response['SecretString']
