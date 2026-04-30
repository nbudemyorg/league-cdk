from http import cookies

import boto3
from aws_lambda_context import LambdaContext
from aws_lambda_typing.events import APIGatewayProxyEventV1
from aws_lambda_typing.responses import APIGatewayProxyResponseV1
from html_layer import access_denied, home_page, server_error
from league.tables.sessions import get_sessions_item, valid_session

db_client = boto3.resource('dynamodb')
sessions_table = db_client.Table('Sessions')


def lambda_handler(
    event: APIGatewayProxyEventV1, context: LambdaContext
) -> APIGatewayProxyResponseV1:

    event_cookies = event.get('headers', False).get('cookie', False)

    if not event_cookies:
        return {
            'statusCode': 401,
            'headers': {
                'Content-Type': 'text/html',
            },
            'body': access_denied,
        }

    received_cookies = cookies.SimpleCookie()
    received_cookies.load(event['headers']['cookie'])
    player_id = received_cookies.get('player_id', None)
    session_id = received_cookies.get('session_id', None)

    if not player_id or not session_id:
        return generate_response(401, access_denied)

    get_response = get_sessions_item(
        sessions_table, player_id.value, session_id.value
    )

    if get_response['success'] is False:
        return generate_response(503, server_error)

    item = get_response.get('item')

    if not item:
        return generate_response(401, access_denied)

    if valid_session(item):
        return generate_response(200, home_page)

    return generate_response(403, access_denied)


def generate_response(http_code: int, body: str) -> APIGatewayProxyResponseV1:
    return {
        'statusCode': http_code,
        'headers': {
            'Content-Type': 'text/html',
        },
        'body': body,
    }
