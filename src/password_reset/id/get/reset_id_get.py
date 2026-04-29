import json
from datetime import UTC, datetime

import boto3
from aws_lambda_context import LambdaContext
from aws_lambda_typing.events import APIGatewayProxyEventV1
from aws_lambda_typing.responses import APIGatewayProxyResponseV1
from html_layer import new_password_form
from league.tables.item_types import ResetItem
from league.tables.password_reset import get_reset_item
from league.tables.response_types import GetResult

db_client = boto3.resource('dynamodb')
reset_table = db_client.Table('PasswordReset')


def lambda_handler(
    event: APIGatewayProxyEventV1, context: LambdaContext
) -> APIGatewayProxyResponseV1:

    path_params = event.get('pathParameters')

    if not path_params:
        return {'statusCode': 400, 'body': json.dumps('Bad Request')}

    reset_id = path_params.get('resetId')

    if not reset_id:
        return {'statusCode': 400, 'body': json.dumps('Bad Request')}

    get_response = get_reset_item(reset_table, reset_id)

    if server_error(get_response):
        return {'statusCode': 500, 'body': json.dumps('Server Error')}

    if not reset_item_found(get_response):
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'text/html',
            },
            'body': 'Reset token not found',
        }

    reset_item = get_response['item']

    if reset_item_still_valid(reset_item):
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'text/html',
            },
            'body': new_password_form,
        }

    return {
        'statusCode': 200,
        'headers': {
            'Content-Type': 'text/html',
        },
        'body': 'Reset token has expired',
    }


def server_error(response: GetResult) -> bool:
    return response['success'] is False


def reset_item_found(response: GetResult) -> bool:
    item = response.get('item')
    return bool(item != {})


def reset_item_still_valid(item: ResetItem) -> bool:
    return datetime.now(UTC) < datetime.fromisoformat(item['expiry'])
