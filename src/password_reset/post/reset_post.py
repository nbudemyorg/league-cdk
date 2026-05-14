from urllib.parse import parse_qs

import boto3
from aws_lambda_context import LambdaContext
from aws_lambda_typing.events import APIGatewayProxyEventV1
from aws_lambda_typing.responses import APIGatewayProxyResponseV1
from league.content.libs import generate_response
from league.logger import get_logger
from league.tables.item.libs import create_reset_item
from league.tables.reset import put_reset_item
from league.tables.users import update_users_item
from league.validate import valid_player_id

SECONDS_VALID = 600

db_client = boto3.resource('dynamodb')
users_table = db_client.Table('Users')
resets_table = db_client.Table('Resets')


def lambda_handler(
    event: APIGatewayProxyEventV1, context: LambdaContext
) -> APIGatewayProxyResponseV1:

    logger = get_logger()

    if isinstance(event['body'], str):
        processed_form = transform_validate(event['body'])
    else:
        logger.warning('Event body not a string. Request Rejected.')
        return silent_fail_response()

    if processed_form['validated'] == 'false':
        logger.warning('Invalid form submission. Request rejected.')
        return silent_fail_response()

    supplied_player_id = processed_form['player_id']

    logger.info(f'Processing request for player_id: {supplied_player_id}.')

    reset_item = create_reset_item(supplied_player_id)

    token = reset_item['reset_id']

    update_response = update_users_item(users_table, supplied_player_id, token)

    if not update_response['success']:
        logger.critical('Failed to update item in Users table.')
        return fail_response()

    put_response = put_reset_item(resets_table, reset_item)

    if not put_response['success']:
        logger.critical('Failed to update item in Resets table.')
        return fail_response()

    logger.info(f'Completed request for player_id: {supplied_player_id}.')
    return success_response()


def transform_validate(body: str) -> dict[str, str]:
    """Transform event body string into a dict"""
    form_data = parse_qs(body)

    transformed_body = {key: value[0] for key, value in form_data.items()}

    player = transformed_body.get('player_id')

    if len(transformed_body) != 1 or not player:
        return {'validated': 'false'}

    if valid_player_id(player):
        transformed_body['validated'] = 'true'
    else:
        transformed_body['validated'] = 'false'

    return transformed_body


def success_response() -> APIGatewayProxyResponseV1:
    return generate_response(200, 'reset_form.html', alert='submitted')


def silent_fail_response() -> APIGatewayProxyResponseV1:
    return success_response()


def fail_response() -> APIGatewayProxyResponseV1:
    return generate_response(503, 'reset_form.html', alert='server')
