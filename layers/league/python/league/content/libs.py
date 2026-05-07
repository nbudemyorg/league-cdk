from typing import Any

from aws_lambda_typing.responses import APIGatewayProxyResponseV1
from jinja2 import Environment, FileSystemLoader

TEMPLATE_DIR = '/opt/python/league/content/templates'


def generate_response(
    status_code: int,
    template_file: str,
    alert: str = 'none',
    params: dict[str, Any] | None = None,
) -> APIGatewayProxyResponseV1:

    if not isinstance(status_code, int):
        raise TypeError(
            f'HTTP Status Code must be an integer: Type={type(status_code)}'
        )
    if not 99 < status_code < 599:
        raise ValueError(f'Invalid HTTP Status Code : {status_code}')
    if not isinstance(alert, str):
        raise TypeError(
            f'Template alert code must be a string: Type={type(alert)}'
        )

    body = render_template(template_file, alert, params)

    return {
        'statusCode': status_code,
        'isBase64Encoded': False,
        'headers': {'Content-Type': 'text/html'},
        'body': body,
    }


def render_template(
    template_file: str, alert: str, params: dict[str, Any] | None
) -> str:
    if params is None:
        params = {'params': 'none'}
    env = Environment(loader=FileSystemLoader(TEMPLATE_DIR))
    template = env.get_template(template_file)
    return template.render(alert=alert, params=params)
