from aws_cdk import Stack
from aws_cdk.aws_apigateway import (
    EndpointConfiguration,
    EndpointType,
    LambdaIntegration,
    RestApi,
)
from constructs import Construct

from league_cdk.events_stack import EventsStack
from league_cdk.layers_stack import LayersStack
from league_cdk.login_registration_stack import LoginRegistrationStack


class LeagueRootStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs):
        super().__init__(scope, construct_id, **kwargs)

        layers_stack = LayersStack(self, 'LayersStack')

        events_stack = EventsStack(
            self, 'EventStack', stack_layers=layers_stack.layers
        )

        login_registration_stack = LoginRegistrationStack(
            self,
            'LoginRegistrationStack',
            events_arn=events_stack.league_bus_arn,
            stack_layers=layers_stack.layers,
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
            'POST', LambdaIntegration(login_registration_stack.login_post)
        )
        login_resource.add_method(
            'GET', LambdaIntegration(login_registration_stack.login_get)
        )

        homepage_resource = league_api.root.add_resource('home')
        homepage_resource.add_method(
            'GET', LambdaIntegration(login_registration_stack.home_get)
        )

        register_resource = league_api.root.add_resource('register')
        register_resource.add_method(
            'POST',
            LambdaIntegration(login_registration_stack.reg_post),
        )
        register_resource.add_method(
            'GET', LambdaIntegration(login_registration_stack.reg_get)
        )

        reset_resource = league_api.root.add_resource('reset')
        reset_resource.add_method(
            'GET',
            LambdaIntegration(login_registration_stack.reset_get),
        )
        reset_resource.add_method(
            'POST', LambdaIntegration(login_registration_stack.reset_post)
        )

        reset_id_resource = reset_resource.add_resource('{resetId}')
        reset_id_resource.add_method(
            'GET', LambdaIntegration(login_registration_stack.reset_id_get)
        )
        reset_id_resource.add_method(
            'POST', LambdaIntegration(login_registration_stack.reset_id_post)
        )
