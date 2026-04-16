import json
from urllib.parse import parse_qs

import bcrypt
import boto3
from auth_layer import create_session_item, valid_player_id
from botocore.exceptions import ClientError
from mypy_boto3_dynamodb.type_defs import GetItemOutputTableTypeDef
from types_boto3_dynamodb.service_resource import Table

db_client = boto3.resource('dynamodb')
users_table = db_client.Table('Users')
sessions_table = db_client.Table('Sessions')


def lambda_handler(event, context):

    user_data = valid_form_data(event['body'])

    if not user_data:
        return {
            'statusCode': 400,
            'body': json.dumps('Invalid form submission'),
        }

    password = user_data['password']
    player_id = user_data['player_id']

    if not valid_player_id(player_id):
        return {'statusCode': 400, 'body': json.dumps('Invalid player ID')}

    if not password_is_valid(users_table, player_id, password):
        return {'statusCode': 401, 'body': json.dumps('Invalid password')}

    session_id = create_session_item(sessions_table, player_id)

    if not session_id:
        return {'statusCode': 500, 'body': json.dumps('Put Item failed')}

    return {
        'statusCode': 301,
        'multiValueHeaders': {
            'Set-Cookie': [
                f'session_id={session_id}',
                f'player_id={player_id}',
            ],
            'Location': ['/prod/home'],
        },
    }


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

    try:
        response: GetItemOutputTableTypeDef = table.get_item(
            Key={'player_id': supplied_id}
        )

    except ClientError:
        return None

    item = response.get('Item')

    if not item:
        return False

    pw_val = item.get('password')

    if pw_val is None:
        return False

    if isinstance(pw_val, bytes):
        stored_bytes = pw_val
    elif isinstance(pw_val, str):
        stored_bytes = pw_val.encode('utf-8')
    else:
        return False

    password_bytes = supplied_password.encode('utf-8')
    return bcrypt.checkpw(password_bytes, stored_bytes)
