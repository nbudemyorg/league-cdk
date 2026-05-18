from pathlib import Path

import yaml
from aws_cdk import Stack
from aws_cdk.aws_events import EventBus
from aws_cdk.aws_lambda import LayerVersion
from constructs import Construct

from lib import lambdas


class EventsStack(Stack):
    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        stack_layers: dict[str, LayerVersion],
        **kwargs,
    ):
        super().__init__(scope, construct_id, **kwargs)

        bus = EventBus(self, 'LeagueEventBus', event_bus_name='league')

        with Path.open('./config/lambdas/events.yaml') as lambdas_yaml:
            lambdas_config = yaml.load(lambdas_yaml, yaml.FullLoader)

        lambda_bundle = {'layers': stack_layers}

        for lambda_dict in lambdas_config['lambdas']:
            property_name = lambda_dict['name']
            new_lambda = lambdas.create_lambda(
                self,
                bundle=lambda_bundle,
                **lambda_dict,
            )

            setattr(self, property_name, new_lambda)

        self.league_bus_arn = bus.event_bus_arn
