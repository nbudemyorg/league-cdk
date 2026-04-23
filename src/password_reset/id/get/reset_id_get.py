import json

from aws_lambda_context import LambdaContext
from aws_lambda_typing.events import APIGatewayProxyEventV1
from aws_lambda_typing.responses import APIGatewayProxyResponseV1
from html_layer import new_password_form


def lambda_handler(
    event: APIGatewayProxyEventV1, context: LambdaContext
) -> APIGatewayProxyResponseV1:

    path_params = event.get('pathParameters')

    if not path_params:
        return {'statusCode': 400, 'body': json.dumps('Bad Request')}

    reset_id = path_params.get('resetId')

    return {
        'statusCode': 200,
        'headers': {
            'Content-Type': 'text/html',
        },
        'body': new_password_form,
    }
