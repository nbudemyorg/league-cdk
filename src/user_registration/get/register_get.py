from aws_lambda_context import LambdaContext
from html_layer import registration_form


def lambda_handler(event: dict, context: LambdaContext) -> dict:

    return {
        'statusCode': 200,
        'headers': {
            'Content-Type': 'text/html',
        },
        'body': registration_form,
    }
