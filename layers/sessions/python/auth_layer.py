import re
from datetime import UTC, datetime, timedelta
from uuid import uuid4

import bcrypt
from aws_lambda_typing.responses import APIGatewayProxyResponseV1
from botocore.exceptions import ClientError
from types_boto3_dynamodb.service_resource import Table

COOKIE_MAX_AGE = 86_400  #  24 * 60 * 60 seconds (1 Day)
ADD_TTL = 60


def create_session_item(table: Table, supplied_id: str) -> str | bool:
    """Creates a new session item for given player_id"""
    session_id = str(uuid4())

    now = datetime.now(UTC)

    session_expiry = now + timedelta(seconds=COOKIE_MAX_AGE)
    item_ttl = int(session_expiry.timestamp() + ADD_TTL)

    session_item = {
        'player_id': supplied_id,
        'session_id': session_id,
        'expiry': session_expiry.isoformat(),
        'ttl': item_ttl,
    }

    try:
        table.put_item(Item=session_item)
    except ClientError:
        return None
    else:
        return session_id


def create_login_response(
    player: str, session: str
) -> APIGatewayProxyResponseV1:

    multi_value_headers = {}

    cookie_section = {
        'Set-Cookie': [
            f'player_id={player}; Max-Age={COOKIE_MAX_AGE}',
            f'session_id={session}; Max-Age={COOKIE_MAX_AGE}',
        ]
    }

    location = {'Location': ['/prod/home']}

    multi_value_headers.update(cookie_section)
    multi_value_headers.update(location)

    return {'statusCode': 301, 'multiValueHeaders': multi_value_headers}


def get_player_item(table: Table, supplied_id: str) -> dict[str, str] | None:
    """Returns item for Player ID if it exists in the Users table."""

    try:
        response = table.get_item(Key={'player_id': supplied_id})

    except ClientError:
        return None
    else:
        if 'Item' in response:
            return response['Item']

        return {'id_not_found': supplied_id}


def generate_password_hash(supplied_password: str) -> str:
    """Generates a bcrypt hash with salt of the supplied password"""

    password_bytes = supplied_password.encode('utf-8')
    password_salt = bcrypt.gensalt()

    password_bytes = bcrypt.hashpw(password_bytes, password_salt)

    return password_bytes.decode()


def valid_session(table: Table, player: str, session: str) -> bool:
    """Given the supplied session_id and player_id, verify a valid session item
    exists for the player in the Sessions table"""

    try:
        response = table.get_item(
            Key={'player_id': player, 'session_id': session},
            AttributesToGet=['expiry'],
        )
    except ClientError:
        return None

    if 'Item' not in response:
        return False

    session_item = response['Item']

    if 'expiry' not in session_item:
        return False

    current_time = datetime.now(UTC)
    session_expiry = datetime.fromisoformat(session_item['expiry'])

    return session_expiry > current_time


def valid_player_id(supplied_id: str) -> bool:
    """Verify supplied player id conforms to either PSN or Xbox restrictions"""
    return bool(valid_psn_id(supplied_id) or valid_xbox_id(supplied_id))


def valid_psn_id(supplied_id: str) -> bool:
    """
    Does the supplied id confirm to PSN restrictions:
    Length: 3-16 characters
    Must start with a letter of the Alphabet
    Characters: Alphanumeric + underscore + hyphens, NO SPACES
    """
    expression = r'^[a-zA-Z][\w-]{2,15}$'

    return bool(re.match(expression, supplied_id))


def valid_xbox_id(supplied_id: str) -> bool:
    """
    Does the supplied id confirm to Xbox Gamertag restrictions:
    Length: 3-12 characters
    Must start with a letter of the Alphabet
    Characters: Alphanumeric + space, NO HYPHEN OR UNDERSCORE
    """
    expression = r'^[a-zA-Z][0-9a-zA-Z\s]{2,11}$'

    return bool(re.match(expression, supplied_id))
