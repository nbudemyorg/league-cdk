from http import cookies

import boto3
from auth_layer import valid_session
from html_layer import access_denied, home_page, server_error

db_client = boto3.resource('dynamodb')
sessions_table = db_client.Table('Sessions')


def lambda_handler(event, context):

    event_cookies = event.get('headers', False).get('cookie', False)

    if not event_cookies:
        return {
            'statusCode': 401,
            'headers': {
                'Content-Type': 'text/html',
            },
            'body': access_denied,
        }

    event_cookies = cookies.SimpleCookie()
    event_cookies.load(event['headers']['cookie'])
    player_id = event_cookies.get('player_id', None)
    session_id = event_cookies.get('session_id', None)

    if not player_id or not session_id:
        return {
            'statusCode': 401,
            'headers': {
                'Content-Type': 'text/html',
            },
            'body': access_denied,
        }

    response = valid_session(sessions_table, player_id.value, session_id.value)

    if response:
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'text/html',
            },
            'body': home_page,
        }

    if response is None:
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'text/html',
            },
            'body': server_error,
        }

    return {
        'statusCode': 403,
        'headers': {
            'Content-Type': 'text/html',
        },
        'body': access_denied,
    }
