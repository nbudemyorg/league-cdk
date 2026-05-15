from http import cookies
from typing import cast

import boto3
from aws_lambda_context import LambdaContext
from aws_lambda_typing.events import APIGatewayProxyEventV1
from aws_lambda_typing.responses import APIGatewayProxyResponseV1
from league.content.libs import generate_response
from league.static.pages import access_denied, home_page, server_error
from league.tables.item.libs import valid_session
from league.tables.item.types import SessionItem
from league.tables.sessions import get_sessions_item

db_client = boto3.resource('dynamodb')
sessions_table = db_client.Table('Sessions')


def lambda_handler(
    event: APIGatewayProxyEventV1, context: LambdaContext
) -> APIGatewayProxyResponseV1:

    event_cookies = event.get('headers', False).get('cookie', False)

    if not event_cookies:
        generate_response(401, 'login_form.html', alert='invalid')

    received_cookies = cookies.SimpleCookie()
    received_cookies.load(event['headers']['cookie'])
    player_id = received_cookies.get('player_id', None)
    session_id = received_cookies.get('session_id', None)

    if not player_id or not session_id:
        generate_response(401, 'login_form.html', alert='invalid')

    get_response = get_sessions_item(
        sessions_table, player_id.value, session_id.value
    )

    if get_response['success'] is False:
        generate_response(503, 'login_form.html', alert='server')

    item = get_response.get('item')

    if not item:
        return generate_response(401, 'login_form.html', alert='credentials')

    if valid_session(cast('SessionItem', item)):
        return generate_response(200, 'home.html')

    return generate_response(403, 'login_form.html', alert='credentials')
