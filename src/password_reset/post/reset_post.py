import secrets
from datetime import UTC, datetime, timedelta
from decimal import Decimal
from typing import cast
from urllib.parse import parse_qs

import boto3
from auth_layer import valid_player_id
from aws_lambda_context import LambdaContext
from aws_lambda_typing.events import APIGatewayProxyEventV1
from aws_lambda_typing.responses import APIGatewayProxyResponseV1
from botocore.exceptions import ClientError
from types_boto3_dynamodb.service_resource import Table

SECONDS_VALID = 600

db_client = boto3.resource('dynamodb')
users_table = db_client.Table('Users')
reset_table = db_client.Table('PasswordReset')


def lambda_handler(
    event: APIGatewayProxyEventV1, context: LambdaContext
) -> APIGatewayProxyResponseV1:

    if isinstance(event['body'], str):
        processed_form = transform_validate(event['body'])
    else:
        return silent_fail_response()

    if processed_form['validated'] == 'false':
        return silent_fail_response()

    player_item = get_player_item(users_table, processed_form['player_id'])

    if not player_item:
        return silent_fail_response()

    updated_player = update_player_item(users_table, player_item, True)

    if not updated_player:
        return fail_response()

    if not create_reset_item(reset_table, updated_player):
        return fail_response()

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
    multi_value_headers = {}
    location = {'Location': ['/prod/login']}
    multi_value_headers.update(location)
    return {'statusCode': 301, 'multiValueHeaders': multi_value_headers}


def silent_fail_response() -> APIGatewayProxyResponseV1:
    return success_response()


def fail_response() -> APIGatewayProxyResponseV1:
    return {'statusCode': 503, 'body': 'Server Error'}


def get_player_item(table: Table, supplied_id: str) -> dict[str, str] | None:
    """Returns item for Player ID if it exists in the Users table."""

    try:
        response = table.get_item(Key={'player_id': supplied_id})

    except ClientError:
        return None
    else:
        if 'Item' in response:
            player_item = response['Item']
            return cast('dict[str, str]', player_item)

        return None


def update_player_item(
    table: Table, item: dict[str, str], reset_token: bool = False
) -> dict[str, str] | None:

    if reset_token:
        token = secrets.token_urlsafe()
        item['reset_id'] = token

    try:
        response = table.put_item(Item=item)

    except ClientError:
        return None

    return item


def create_reset_item(
    table: Table, player_item: dict[str, str]
) -> bool | None:

    player: str = player_item['player_id']
    token: str = player_item['reset_id']
    expiry = datetime.now(UTC) + timedelta(seconds=SECONDS_VALID)
    expiry_string: str = expiry.isoformat()
    item_ttl = Decimal(expiry.timestamp())

    reset_item: dict[str, str | Decimal] = {
        'reset_id': token,
        'player_id': player,
        'expiry': expiry_string,
        'ttl': item_ttl,
    }

    try:
        table.put_item(Item=reset_item)

    except ClientError:
        return None

    return True
