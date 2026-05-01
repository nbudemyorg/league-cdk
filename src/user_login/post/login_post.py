import json
from typing import cast
from urllib.parse import parse_qs

import bcrypt
import boto3
from aws_lambda_context import LambdaContext
from aws_lambda_typing.events import APIGatewayProxyEventV1
from aws_lambda_typing.responses import APIGatewayProxyResponseV1
from league.auth import create_login_response
from league.tables.item.libs import create_session_item
from league.tables.item.types import UserItem
from league.tables.sessions import put_sessions_item
from league.tables.users import get_users_item
from league.validate import valid_player_id
from types_boto3_dynamodb.service_resource import Table

db_client = boto3.resource('dynamodb')
users_table = db_client.Table('Users')
sessions_table = db_client.Table('Sessions')


def lambda_handler(
    event: APIGatewayProxyEventV1, context: LambdaContext
) -> APIGatewayProxyResponseV1:

    if isinstance(event['body'], str):
        user_data = valid_form_data(event['body'])
    else:
        user_data = None

    if not user_data:
        return {
            'statusCode': 400,
            'body': json.dumps('Invalid form submission'),
        }

    password = user_data['password']
    player_id = user_data['player_id']

    if not valid_player_id(player_id):
        return {'statusCode': 400, 'body': json.dumps('Invalid player ID')}

    valid_password = password_is_valid(users_table, player_id, password)

    if valid_password is False:
        return {'statusCode': 401, 'body': json.dumps('Invalid password')}
    if valid_password is None:
        return {'statusCode': 500, 'body': json.dumps('Server Error')}

    session_item = create_session_item(player_id)

    put_response = put_sessions_item(sessions_table, session_item)

    if not put_response['success']:
        return {
            'statusCode': 500,
            'body': json.dumps('Server Error: Put Item failed'),
        }

    session_id = session_item['session_id']

    return cast(
        'APIGatewayProxyResponseV1',
        create_login_response(player_id, session_id),
    )


def valid_form_data(event_body: str) -> dict[str, str] | None:
    """Test supplied form data for expected params"""

    user_data = parse_qs(event_body)

    transformed_data = {key: value[0] for key, value in user_data.items()}

    player = transformed_data.get('player_id', False)
    password = transformed_data.get('password', False)

    if not player or not password:
        return None

    if not isinstance(player, str) or not isinstance(password, str):
        return None

    return transformed_data


def password_is_valid(
    table: Table, supplied_id: str, supplied_password: str
) -> bool | None:
    """Verify supplied password matches that stored in db using bcrypt"""

    get_response = get_users_item(table, supplied_id)

    if get_response['success'] is True:
        stored_item = cast('UserItem', get_response.get('item'))
        if stored_item:
            stored_password_bytes = stored_item['password'].encode('utf-8')
            posted_password_bytes = supplied_password.encode('utf-8')
            return bcrypt.checkpw(posted_password_bytes, stored_password_bytes)

        return False

    return None
