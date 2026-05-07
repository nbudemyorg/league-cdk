from datetime import UTC, datetime
from typing import TypeGuard, cast

import boto3
from aws_lambda_context import LambdaContext
from aws_lambda_typing.events import APIGatewayProxyEventV1
from aws_lambda_typing.responses import APIGatewayProxyResponseV1
from league.content.libs import generate_response
from league.tables.item.types import ResetItem
from league.tables.reset import get_reset_item
from league.tables.response.types import GetItemSuccess, GetResult

db_client = boto3.resource('dynamodb')
reset_table = db_client.Table('PasswordReset')


def is_get_item_success(response: GetResult) -> TypeGuard[GetItemSuccess]:
    return response['success'] is True


def lambda_handler(
    event: APIGatewayProxyEventV1, context: LambdaContext
) -> APIGatewayProxyResponseV1:
    path_params = event.get('pathParameters')

    if not path_params:
        return reset_fail_response()

    reset_id = path_params.get('resetId')

    if not reset_id:
        return reset_fail_response()

    get_response: GetResult = get_reset_item(reset_table, reset_id)

    if is_get_item_success(get_response):
        reset_item = cast('ResetItem', get_response['item'])

        if not reset_item:
            return reset_fail_response()

        if reset_item_still_valid(reset_item):
            reset_id_value = reset_item['reset_id']
            params = {'reset_id': reset_id_value}
            return generate_response(200, 'password_form.html', params=params)

        return reset_fail_response()

    return generate_response(503, 'reset_form.html', alert='server')


def reset_item_still_valid(item: ResetItem) -> bool:
    return datetime.now(UTC) < datetime.fromisoformat(item['expiry'])


def reset_fail_response() -> APIGatewayProxyResponseV1:
    return generate_response(200, 'reset_form.html', alert='expired')
