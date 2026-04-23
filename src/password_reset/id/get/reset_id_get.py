import json
from datetime import UTC, datetime

import boto3
from auth_layer import get_reset_item
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

    if not reset_id:
        return {'statusCode': 400, 'body': json.dumps('Bad Request')}

    stored_item = get_reset_item(reset_table, reset_id)

    if stored_item is None:
        return {'statusCode': 500, 'body': json.dumps('Server Error')}

    if stored_item.get('item_not_found'):
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'text/html',
            },
            'body': 'Reset token not found',
        }

    if reset_item_still_valid(stored_item):
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


def reset_item_still_valid(item: dict[str, str]) -> bool:

    return datetime.now(UTC) < datetime.fromisoformat(item['expiry'])
