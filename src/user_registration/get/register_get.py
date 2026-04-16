from html_layer import registration_form


def lambda_handler(event, context):

    return {
        'statusCode': 200,
        'headers': {
            'Content-Type': 'text/html',
        },
        'body': registration_form,
    }
