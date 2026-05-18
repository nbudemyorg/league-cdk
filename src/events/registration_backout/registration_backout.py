from aws_lambda_context import LambdaContext
from aws_lambda_typing.events import APIGatewayProxyEventV1
from aws_lambda_typing.responses import APIGatewayProxyResponseV1


def lambda_handler(
    event: APIGatewayProxyEventV1, context: LambdaContext
) -> APIGatewayProxyResponseV1:
    print(event)
    return {
        'statusCode': 200,
        'isBase64Encoded': False,
        'headers': {'Content-Type': 'text/html'},
        'body': '<h1>MyPy Fudge</h1>',
    }
