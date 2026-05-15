import re
from urllib.parse import parse_qs

import boto3
from aws_lambda_context import LambdaContext
from aws_lambda_typing.events import APIGatewayProxyEventV1
from aws_lambda_typing.responses import APIGatewayProxyResponseV1
from email_validator import EmailNotValidError, validate_email
from jinja2 import Environment, FileSystemLoader
from league.auth import create_login_response
from league.aws_secrets import INVITE_SECRET
from league.content.libs import generate_response
from league.credentials import generate_password_hash
from league.logger import get_logger
from league.tables.item.libs import create_session_item, create_user_item
from league.tables.response.types import PutResult
from league.tables.sessions import put_sessions_item
from league.tables.users import put_users_item
from league.validate import password_meets_criteria, valid_player_id

TEST_EMAIL_DELIVERY = True

db_client = boto3.resource('dynamodb')
users_table = db_client.Table('Users')
sessions_table = db_client.Table('Sessions')


def lambda_handler(
    event: APIGatewayProxyEventV1, context: LambdaContext
) -> APIGatewayProxyResponseV1:

    logger = get_logger()

    if isinstance(event['body'], str):
        event_body = form_data_valid(event['body'], TEST_EMAIL_DELIVERY)
    else:
        event_body = None

    if not event_body:
        return generate_response(400, 'register_form.html', alert='invalid')

    supplied_email = event_body['email']
    supplied_invite = event_body['invite']
    supplied_player_id = event_body['player_id']
    supplied_player_password = event_body['password']
    logger.info(f'Registration submitted for player_id: {supplied_player_id}.')

    if not valid_invitation_key(supplied_invite):
        logger.warning(f'Invalid invitation key supplied: {supplied_invite}.')
        return generate_response(401, 'register_form.html', alert='key')

    if not valid_player_id(supplied_player_id):
        logger.warning('Player ID is not valid PSNID or Xbox Gamertag.')
        return generate_response(400, 'register_form.html', alert='player_id')

    if not password_meets_criteria(
        supplied_player_password, supplied_player_id
    ):
        logger.info('Password != required standard. Request rejected.')
        return generate_response(400, 'register_form.html', alert='password')

    hashed_password = generate_password_hash(supplied_player_password)

    user_item = create_user_item(
        supplied_player_id, hashed_password, supplied_email
    )

    put_response = put_users_item(users_table, user_item)

    user_exists = user_already_exists(put_response)

    if user_exists:
        logger.info('Application rejected, player_id is already registered.')
        return generate_response(401, 'register_form.html', alert='exists')

    if user_exists is None:
        logger.critical('Failed to store submitted data in Users table')
        return generate_response(503, 'register_form.html', alert='server')

    session_item = create_session_item(supplied_player_id)

    put_response = put_sessions_item(sessions_table, session_item)

    if not put_response['success']:
        logger.critical('Failed to create new session Users table')
        return generate_response(503, 'register_form.html', alert='server')

    logger.info('Registration process completed.')
    return create_login_response(
        supplied_player_id, session_item['session_id']
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

    return bool(supplied_key == INVITE_SECRET)


def render_template(error_code: str = 'ok') -> str:
    env = Environment(loader=FileSystemLoader('/opt/python/league/templates'))
    template = env.get_template('register_form.html')
    return template.render(error=error_code)
