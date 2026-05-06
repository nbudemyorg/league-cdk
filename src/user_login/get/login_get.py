from aws_lambda_context import LambdaContext
from aws_lambda_typing.events import APIGatewayProxyEventV1
from aws_lambda_typing.responses import APIGatewayProxyResponseV1
from jinja2 import Environment, FileSystemLoader


def lambda_handler(
    event: APIGatewayProxyEventV1, context: LambdaContext
) -> APIGatewayProxyResponseV1:

    rendered_template = render_template()

    return {
        'statusCode': 200,
        'headers': {
            'Content-Type': 'text/html',
        },
        'body': rendered_template,
    }


def render_template() -> str:
    env = Environment(loader=FileSystemLoader('/opt/python/league/templates'))
    template = env.get_template('login_form.html')
    return template.render(error=None)
