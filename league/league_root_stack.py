from aws_cdk import Stack
from aws_cdk.aws_apigateway import (
    EndpointConfiguration,
    EndpointType,
    LambdaIntegration,
    RestApi,
)
from constructs import Construct

from league.login_registration_stack import LoginRegistrationStack


class LeagueRootStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs):
        super().__init__(scope, construct_id, **kwargs)

        login_registration_stack = LoginRegistrationStack(
            self, 'LoginRegistrationStack'
        )

        api_config = EndpointConfiguration(types=[EndpointType.REGIONAL])

        league_api = RestApi(
            self,
            'LeagueAPI',
            rest_api_name='LeagueAPI',
            endpoint_configuration=api_config,
        )

        login_resource = league_api.root.add_resource('login')
        login_resource.add_method(
            'POST', LambdaIntegration(login_registration_stack.login_lambda)
        )
        login_resource.add_method(
            'GET', LambdaIntegration(login_registration_stack.login_lambda_get)
        )

        homepage_resource = league_api.root.add_resource('home')
        homepage_resource.add_method(
            'GET', LambdaIntegration(login_registration_stack.home_page_lambda)
        )

        register_resource = league_api.root.add_resource('register')
        register_resource.add_method(
            'POST',
            LambdaIntegration(login_registration_stack.registration_lambda),
        )
        register_resource.add_method(
            'GET',
            LambdaIntegration(
                login_registration_stack.registration_lambda_get
            ),
        )
