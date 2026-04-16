from html_layer import login_form


def lambda_handler(event, context):

    return {
        'statusCode': 200,
        'headers': {
            'Content-Type': 'text/html',
        },
        'body': login_form,
    }
