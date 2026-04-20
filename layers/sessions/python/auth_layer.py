import re
from datetime import UTC, datetime, timedelta
from http import cookies
from uuid import uuid4

from botocore.exceptions import ClientError

COOKIE_MAX_AGE = 864_000 #  24 * 60 * 60 seconds (1 Day)


def create_session_item(table, supplied_id: str) -> str | bool:
    """Creates a new session item for given player_id"""
    session_id = str(uuid4())
    print(session_id)
    session_item = {'player_id': supplied_id, 'session_id': session_id}

    try:
        table.put_item(Item=session_item)
    except ClientError:
        return None
    else:
        return session_id


def create_login_response(player: str, session: str) -> dict[str, list[str]]:

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

    return {
        'statusCode': 301,
        'multiValueHeaders': multi_value_headers
    }


def valid_session(table, player: str, session: str) -> bool:
    """Given the supplied session_id and player_id, verify a valid session item
    exists for the player in the Sessions table"""

    try:
        response = table.get_item(
            Key={'player_id': player, 'session_id': session}
        )
    except ClientError:
        return None

    return 'Item' in response


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
