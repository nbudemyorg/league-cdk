import json
from datetime import UTC, datetime
from typing import Any, TypeGuard, cast

import boto3
from aws_lambda_context import LambdaContext
from aws_lambda_typing.events import APIGatewayProxyEventV1
from aws_lambda_typing.responses import APIGatewayProxyResponseV1
from jinja2 import Environment, FileSystemLoader
from league.tables.item.types import ResetItem
from league.tables.reset import get_reset_item
from league.tables.response.types import GetItemSuccess, GetResult

db_client = boto3.resource('dynamodb')
reset_table = db_client.Table('PasswordReset')

from typing import TypeGuard

def is_get_item_success(response: GetResult) -> TypeGuard[GetItemSuccess]:
    return response['success'] is True

def lambda_handler(
    event: APIGatewayProxyEventV1,
    context: LambdaContext
) -> APIGatewayProxyResponseV1:
    path_params = event.get('pathParameters')

    if not path_params:
        return {'statusCode': 400, 'body': json.dumps('Bad Request')}

    reset_id = path_params.get('resetId')
    if not reset_id:
        return {'statusCode': 400, 'body': json.dumps('Bad Request')}

    get_response: GetResult = get_reset_item(reset_table, reset_id)

    if is_get_item_success(get_response):
        reset_item = cast(ResetItem, get_response['item'])

        if not reset_item:
            return {
                'statusCode': 200,
                'headers': {'Content-Type': 'text/html'},
                'body': 'Reset token not found',
            }

        if reset_item_still_valid(reset_item):
            reset_id_value = reset_item['reset_id']
            env = Environment(loader=FileSystemLoader('/opt/python/league/templates'))
            template = env.get_template('change_password.html')
            rendered_html = template.render(reset_id=reset_id_value)
            return {
                'statusCode': 200,
                'headers': {'Content-Type': 'text/html'},
                'body': rendered_html,
            }

        return {
            'statusCode': 200,
            'headers': {'Content-Type': 'text/html'},
            'body': 'Reset token not found',
        }

    return {'statusCode': 500, 'body': json.dumps('Server Error')}


def reset_item_still_valid(item: ResetItem) -> bool:
    return datetime.now(UTC) < datetime.fromisoformat(item['expiry'])
