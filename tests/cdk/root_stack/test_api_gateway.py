import aws_cdk as core
import aws_cdk.assertions as assertions

from league.league_root_stack import LeagueRootStack

app = core.App()
stack = LeagueRootStack(app, 'league')
template = assertions.Template.from_stack(stack)


def test_api_gateway_count():
    template.resource_count_is('AWS::ApiGateway::RestApi', 1)


def test_api_has_expected_name():
    template.has_resource_properties(
        'AWS::ApiGateway::RestApi', {'Name': 'LeagueAPI'}
    )


def test_prod_stage_created():
    template.has_resource_properties(
        'AWS::ApiGateway::Stage', {'StageName': 'prod'}
    )


def test_api_is_regional_deployment():
    template.has_resource_properties(
        'AWS::ApiGateway::RestApi',
        {'EndpointConfiguration': {'Types': ['REGIONAL']}},
    )


def test_api_has_login_resource():
    template.has_resource_properties(
        'AWS::ApiGateway::Resource', {'PathPart': 'login'}
    )


def test_api_post_login_lambda_permission():
    template.has_resource_properties(
        'AWS::Lambda::Permission',
        assertions.Match.object_like(
            {
                'Action': 'lambda:InvokeFunction',
                'Principal': 'apigateway.amazonaws.com',
                'SourceArn': {
                    'Fn::Join': [
                        '',
                        assertions.Match.array_with(['/POST/login']),
                    ]
                },
            }
        ),
    )


def test_api_get_login_lambda_permission():
    template.has_resource_properties(
        'AWS::Lambda::Permission',
        assertions.Match.object_like(
            {
                'Action': 'lambda:InvokeFunction',
                'Principal': 'apigateway.amazonaws.com',
                'SourceArn': {
                    'Fn::Join': [
                        '',
                        assertions.Match.array_with(['/GET/login']),
                    ]
                },
            }
        ),
    )


def test_api_has_home_resource():
    template.has_resource_properties(
        'AWS::ApiGateway::Resource', {'PathPart': 'home'}
    )


def test_api_get_home_lambda_permission():
    template.has_resource_properties(
        'AWS::Lambda::Permission',
        assertions.Match.object_like(
            {
                'Action': 'lambda:InvokeFunction',
                'Principal': 'apigateway.amazonaws.com',
                'SourceArn': {
                    'Fn::Join': [
                        '',
                        assertions.Match.array_with(['/GET/home']),
                    ]
                },
            }
        ),
    )


def test_api_has_register_resource():
    template.has_resource_properties(
        'AWS::ApiGateway::Resource', {'PathPart': 'register'}
    )


def test_api_post_register_lambda_permission():
    template.has_resource_properties(
        'AWS::Lambda::Permission',
        assertions.Match.object_like(
            {
                'Action': 'lambda:InvokeFunction',
                'Principal': 'apigateway.amazonaws.com',
                'SourceArn': {
                    'Fn::Join': [
                        '',
                        assertions.Match.array_with(['/POST/register']),
                    ]
                },
            }
        ),
    )


def test_api_get_register_lambda_permission():
    template.has_resource_properties(
        'AWS::Lambda::Permission',
        assertions.Match.object_like(
            {
                'Action': 'lambda:InvokeFunction',
                'Principal': 'apigateway.amazonaws.com',
                'SourceArn': {
                    'Fn::Join': [
                        '',
                        assertions.Match.array_with(['/GET/register']),
                    ]
                },
            }
        ),
    )
