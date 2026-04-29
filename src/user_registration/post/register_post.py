import json
import re
from typing import cast
from urllib.parse import parse_qs

import boto3
from auth_layer import (
    create_login_response,
    generate_password_hash,
    valid_player_id,
)
from aws_lambda_context import LambdaContext
from aws_lambda_typing.events import APIGatewayProxyEventV1
from aws_lambda_typing.responses import APIGatewayProxyResponseV1
from botocore.exceptions import ClientError
from email_validator import EmailNotValidError, validate_email
from league.tables.item_libs import create_session_item, create_user_item
from league.tables.response_types import PutResult
from league.tables.sessions import put_sessions_item
from league.tables.users import put_users_item

TEST_EMAIL_DELIVERY = True

secret_name = 'league/invitation_key'
region_name = 'eu-west-1'

# Create a Secrets Manager client
client = boto3.client(service_name='secretsmanager', region_name=region_name)

try:
    get_secret_value_response = client.get_secret_value(SecretId=secret_name)

except ClientError as e:
    raise e

secret = get_secret_value_response['SecretString']

db_client = boto3.resource('dynamodb')
users_table = db_client.Table('Users')
sessions_table = db_client.Table('Sessions')


def lambda_handler(
    event: APIGatewayProxyEventV1, context: LambdaContext
) -> APIGatewayProxyResponseV1:

    if isinstance(event['body'], str):
        event_body = form_data_valid(event['body'], TEST_EMAIL_DELIVERY)
    else:
        event_body = None

    if not event_body:
        return {'statusCode': 400, 'body': json.dumps('Invalid Request')}

    supplied_email = event_body['email']
    supplied_invite = event_body['invite']
    supplied_player_id = event_body['player_id']
    supplied_player_password = event_body['password']

    if not valid_invitation_key(supplied_invite):
        return {
            'statusCode': 400,
            'body': json.dumps('Invalid Invitation Key'),
        }

    if not valid_player_id(supplied_player_id):
        return {'statusCode': 400, 'body': json.dumps('Invalid player ID')}

    if not password_meets_criteria(
        supplied_player_password, supplied_player_id
    ):
        return {
            'statusCode': 400,
            'body': json.dumps('Invalid password supplied'),
        }

    hashed_password = generate_password_hash(supplied_player_password)

    user_item = create_user_item(
        supplied_player_id, hashed_password, supplied_email
    )

    put_response = put_users_item(users_table, user_item)

    user_exists = user_already_exists(put_response)

    if user_exists:
        return {
            'statusCode': 400,
            'body': json.dumps('Player ID already registered'),
        }

    if user_exists is None:
        return {
            'statusCode': 500,
            'body': json.dumps('Server Error: Put Item failed'),
        }

    session_item = create_session_item(supplied_player_id)

    put_response = put_sessions_item(sessions_table, session_item)

    if not put_response['success']:
        return {
            'statusCode': 500,
            'body': json.dumps('Server Error: Put Item failed'),
        }

    return cast(
        'APIGatewayProxyResponseV1',
        create_login_response(supplied_player_id, session_item['session_id']),
    )


def form_data_valid(
    form_data: str, check_delivery: bool
) -> dict[str, str] | None:
    """Inspect supplied message body to ensure all required fields have been
    supplied via the HTML form"""

    user_data = parse_qs(form_data)

    transformed_data = {key: value[0] for key, value in user_data.items()}

    invite = transformed_data.get('invite')
    player_id = transformed_data.get('player_id')
    password = transformed_data.get('password')
    email = transformed_data.get('email', 'invalid')

    if not all([invite, player_id, password, email]):
        return None

    try:
        email_info = validate_email(email, check_deliverability=check_delivery)
        transformed_data['email'] = email_info.normalized

    except EmailNotValidError as e:
        print(str(e))
        return None

    if (
        isinstance(invite, str)
        and isinstance(player_id, str)
        and isinstance(password, str)
    ):
        return transformed_data

    return None


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


def user_already_exists(response: PutResult) -> bool | None:
    if response['success']:
        return False

    error_code = response.get('error_code')
    if error_code == 'ConditionalCheckFailedException':
        return True

    return None


def valid_invitation_key(supplied_key: str) -> bool:
    """Verify the new player supplied the correct invitation key before
    allowing registration"""

    return supplied_key == secret
