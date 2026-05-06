from aws_lambda_typing.responses import APIGatewayProxyResponseV1

COOKIE_MAX_AGE = 86_400  #  24 * 60 * 60 seconds (1 Day)
ADD_TTL = 60


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
