import json

import boto3
from auth_layer import reset_item_valid
from aws_lambda_context import LambdaContext
from aws_lambda_typing.events import APIGatewayProxyEventV1
from aws_lambda_typing.responses import APIGatewayProxyResponseV1
from html_layer import new_password_form

db_client = boto3.resource('dynamodb')
reset_table = db_client.Table('PasswordReset')


def lambda_handler(
    event: APIGatewayProxyEventV1, context: LambdaContext
) -> APIGatewayProxyResponseV1:

    path_params = event.get('pathParameters')

    if not path_params:
        return {'statusCode': 400, 'body': json.dumps('Bad Request')}

    reset_id = path_params.get('resetId')

    reset_allowed = reset_item_valid(reset_table, reset_id)
    if reset_allowed:
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'text/html',
            },
            'body': new_password_form,
        }

    if reset_allowed is False:
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'text/html',
            },
            'body': 'Reset token expired',
        }

    return {'statusCode': 400, 'body': json.dumps('Server Error')}
