import re
from datetime import UTC, datetime
from typing import TypeGuard
from urllib.parse import parse_qs

import boto3
from aws_lambda_context import LambdaContext
from aws_lambda_typing.events import APIGatewayProxyEventV1
from aws_lambda_typing.responses import APIGatewayProxyResponseV1
from league.content.libs import generate_response
from league.credentials import generate_password_hash
from league.logger import get_logger
from league.tables.item.libs import create_user_item, reset_item_expired
from league.tables.reset import delete_reset_item, get_reset_item
from league.tables.response.types import (
    GetItemSuccess,
    GetResult,
)
from league.tables.users import get_users_item, put_users_item
from league.validate import password_meets_criteria

db_client = boto3.resource('dynamodb')
resets_table = db_client.Table('Resets')
users_table = db_client.Table('Users')


def get_operation_success(response: GetResult) -> TypeGuard[GetItemSuccess]:
    return response['success'] is True


def lambda_handler(
    event: APIGatewayProxyEventV1, context: LambdaContext
) -> APIGatewayProxyResponseV1:

    logger = get_logger()

    event_dict = process_event(event)

    if any(value == 'missing' for value in event_dict.values()):
        logger.warning(f'Missing form data: {event_dict}. Request rejected.')
        return generate_response(200, 'reset_form.html', alert='unexpected')

    reset_id = event_dict['reset_id']
    new_password = event_dict['new_password']

    logger.info(f'Processing reset id {reset_id}')

    get_reset_response: GetResult = get_reset_item(resets_table, reset_id)

    if not get_operation_success(get_reset_response):
        logger.critical('Failed to retrieve item from Resets table.')
        return server_error_response()

    reset_item = get_reset_response['item']
    reset_player_id = reset_item['player_id']

    if reset_item_expired(reset_item):
        logger.info('Supplied reset id has expired. Request rejected.')
        return generate_response(200, 'reset_form.html', alert='expired')

    if not password_meets_criteria(new_password, reset_player_id):
        params = {'reset_id': reset_id}
        logger.info('Password != required standard. Request rejected.')
        return generate_response(
            200, 'password_form.html', alert='password', params=params
        )

    get_user_response: GetResult = get_users_item(users_table, reset_player_id)

    if not get_operation_success(get_user_response):
        logger.critical('Failed to retrieve item from Users table.')
        return server_error_response()

    users_item = get_user_response['item']

    if users_item['reset_id'] != reset_id:
        logger.warning('Reset id != stored reset id. Request rejected.')
        return generate_response(200, 'reset_form.html', alert='unexpected')

    hashed_password = generate_password_hash(new_password)

    email = users_item['email']

    new_user_item = create_user_item(reset_player_id, hashed_password, email)

    put_user_response = put_users_item(
        users_table, new_user_item, conditional=False
    )

    if not put_user_response['success']:
        logger.critical('Failed to put updated user item in Users table.')
        return server_error_response()

    delete_response = delete_reset_item(resets_table, reset_id)

    if not delete_response['success']:
        logger.critical('Failed to delete reset item from Resets table.')
        return server_error_response()

    logger.info(f'Password reset completed for user: {reset_player_id}')
    return generate_response(200, 'login_form.html', alert='password')


def process_event(event: APIGatewayProxyEventV1) -> dict[str, str]:
    event_data = {}

    event_path_params = event.get('pathParameters')

    if not event_path_params:
        event_data['reset_id'] = 'missing'
    else:
        reset_id = event_path_params.get('resetId')
        if not reset_id:
            event_data['reset_id'] = 'missing'
        else:
            event_data['reset_id'] = reset_id

    event_body = event.get('body')

    if not event_body:
        event_data['new_password'] = 'missing'
    else:
        form_data = parse_qs(event_body)
        transformed_data = {key: value[0] for key, value in form_data.items()}
        new_password = transformed_data.get('new_password')
        if not new_password:
            event_data['new_password'] = 'missing'
        else:
            event_data['new_password'] = new_password

    return event_data


def server_error_response() -> APIGatewayProxyResponseV1:
    return generate_response(503, 'reset_form.html', alert='server')
