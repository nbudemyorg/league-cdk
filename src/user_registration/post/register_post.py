import json
import re
from typing import cast
from urllib.parse import parse_qs

import bcrypt
import boto3
from auth_layer import (
    create_login_response,
    create_session_item,
    valid_player_id,
)
from aws_lambda_context import LambdaContext
from aws_lambda_typing.events import APIGatewayProxyEventV1
from aws_lambda_typing.responses import APIGatewayProxyResponseV1
from botocore.exceptions import ClientError
from email_validator import EmailNotValidError, validate_email
from types_boto3_dynamodb.service_resource import Table

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

    already_existing_player = player_id_exists(users_table, supplied_player_id)

    if already_existing_player:
        return {
            'statusCode': 400,
            'body': json.dumps('Player ID already registered'),
        }

    if already_existing_player is None:
        return {
            'statusCode': 500,
            'body': json.dumps('Server Error: Get Item failed'),
        }

    hashed_password = generate_password_hash(supplied_player_password)

    if not create_user_item(
        users_table, supplied_player_id, hashed_password, supplied_email
    ):
        return {
            'statusCode': 500,
            'body': json.dumps('Server Error: Put Item failed'),
        }

    session_id = create_session_item(sessions_table, supplied_player_id)

    if not session_id:
        return {'statusCode': 500, 'body': json.dumps('Put Item failed')}

    return cast(
        'APIGatewayProxyResponseV1',
        create_login_response(supplied_player_id, session_id),
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


def create_user_item(
    table: Table, supplied_id: str, hashed_password: str, email: str
) -> bool:
    """Creates a new item in the users table holding the Player ID
    and hashed password"""

    user_db_item = {
        'player_id': supplied_id,
        'password': hashed_password,
        'email': email,
    }

    try:
        table.put_item(Item=user_db_item)
    except ClientError:
        return False
    else:
        return True


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


def player_id_exists(table: Table, supplied_id: str) -> bool | None:
    """Makes sure the supplied Player ID is not already stored in
    the user table."""

    try:
        response = table.get_item(Key={'player_id': supplied_id})

    except ClientError:
        return None
    else:
        return 'Item' in response


def generate_password_hash(supplied_password: str) -> str:
    """Generates a bcrypt hash with salt of the supplied password"""

    password_bytes = supplied_password.encode('utf-8')
    password_salt = bcrypt.gensalt()

    password_bytes = bcrypt.hashpw(password_bytes, password_salt)

    return password_bytes.decode()


def valid_invitation_key(supplied_key: str) -> bool:
    """Verify the new player supplied the correct invitation key before
    allowing registration"""

    return supplied_key == secret
