from typing import TypeGuard, cast

import boto3
from aws_lambda_context import LambdaContext
from aws_lambda_typing.events import APIGatewayProxyEventV1
from aws_lambda_typing.responses import APIGatewayProxyResponseV1
from league.content.libs import generate_response
from league.logger import get_logger
from league.tables.item.libs import reset_item_expired
from league.tables.item.types import ResetItem
from league.tables.reset import get_reset_item
from league.tables.response.types import GetItemSuccess, GetResult

db_client = boto3.resource('dynamodb')
resets_table = db_client.Table('Resets')


def is_get_item_success(response: GetResult) -> TypeGuard[GetItemSuccess]:
    return response['success'] is True


def lambda_handler(
    event: APIGatewayProxyEventV1, context: LambdaContext
) -> APIGatewayProxyResponseV1:

    logger = get_logger()

    path_params = event.get('pathParameters')

    if not path_params:
        logger.warning('No path parameters in event. Request rejected.')
        return reset_fail_response()

    reset_id = path_params.get('resetId')

    if not reset_id:
        logger.warning('No reset id provided. Request rejected.')
        return reset_fail_response()

    get_response: GetResult = get_reset_item(resets_table, reset_id)

    if is_get_item_success(get_response):
        reset_item = cast('ResetItem', get_response['item'])

        if not reset_item:
            logger.info('No valid reset id found. Request rejected.')
            return reset_fail_response()

        if not reset_item_expired(reset_item):
            reset_id_value = reset_item['reset_id']
            params = {'reset_id': reset_id_value}
            logger.info(f'Valid reset id {reset_id}. Serving password form.')
            return generate_response(200, 'password_form.html', params=params)

        logger.info(f'Invalid reset id {reset_id}. Request rejected.')
        return reset_fail_response()

    logger.critical('Failed to retrieve item from Resets table.')
    return generate_response(503, 'reset_form.html', alert='server')


def reset_fail_response() -> APIGatewayProxyResponseV1:
    return generate_response(200, 'reset_form.html', alert='expired')
