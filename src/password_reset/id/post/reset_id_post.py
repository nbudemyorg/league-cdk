import json
import re
from datetime import UTC, datetime
from typing import TypeGuard
from urllib.parse import parse_qs

import boto3
from aws_lambda_context import LambdaContext
from aws_lambda_typing.events import APIGatewayProxyEventV1
from aws_lambda_typing.responses import APIGatewayProxyResponseV1
from league.credentials import generate_password_hash
from league.tables.item.libs import create_user_item
from league.tables.reset import delete_reset_item, get_reset_item
from league.tables.response.types import (
    GetItemSuccess,
    GetResult,
)
from league.tables.users import get_users_item, put_users_item

db_client = boto3.resource('dynamodb')
reset_table = db_client.Table('PasswordReset')
users_table = db_client.Table('Users')


def get_operation_success(response: GetResult) -> TypeGuard[GetItemSuccess]:
    return response['success'] is True


def lambda_handler(
    event: APIGatewayProxyEventV1, context: LambdaContext
) -> APIGatewayProxyResponseV1:

    event_dict = process_event(event)

    if any(value == 'missing' for value in event_dict.values()):
        return {'statusCode': 400, 'body': json.dumps('Bad Request')}

    reset_id = event_dict['reset_id']
    new_password = event_dict['new_password']

    get_reset_response: GetResult = get_reset_item(reset_table, reset_id)

    if not get_operation_success(get_reset_response):
        return {'statusCode': 503, 'body': json.dumps('Server Error')}

    reset_item = get_reset_response['item']
    item_expiry = reset_item['expiry']
    reset_player_id = reset_item['player_id']

    if reset_item_expired(item_expiry):
        return {'statusCode': 200, 'body': json.dumps('Token Expired')}

    if not password_meets_criteria(new_password, reset_player_id):
        return {'statusCode': 400, 'body': json.dumps('Bad Password')}

    get_user_response: GetResult = get_users_item(users_table, reset_player_id)

    if not get_operation_success(get_user_response):
        return {'statusCode': 503, 'body': json.dumps('Server Error')}

    users_item = get_user_response['item']

    if users_item['reset_id'] != reset_id:
        return {'statusCode': 200, 'body': json.dumps('Unexpected Error')}

    hashed_password = generate_password_hash(new_password)

    email = users_item['email']

    new_user_item = create_user_item(reset_player_id, hashed_password, email)

    put_user_response = put_users_item(
        users_table, new_user_item, conditional=False
    )

    if not put_user_response['success']:
        return {'statusCode': 503, 'body': json.dumps('Server Error')}

    delete_response = delete_reset_item(reset_table, reset_id)

    if not delete_response['success']:
        return {'statusCode': 503, 'body': json.dumps('Server Error')}

    return {'statusCode': 200, 'body': json.dumps('Password Reset')}


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


def reset_item_expired(expiry: str) -> bool:
    return datetime.now(UTC) > datetime.fromisoformat(expiry)


def password_meets_criteria(
    supplied_password: str, supplied_player: str
) -> bool:
    """Verifies the supplied password conforms to defined password standards"""

    if len(supplied_password) < 10:
        return False

    if re.search('[0-9]', supplied_password) is None:
        return False

    if re.search('[A-Z]', supplied_password) is None:
        return False

    return not re.search(supplied_player.lower(), supplied_password.lower())
