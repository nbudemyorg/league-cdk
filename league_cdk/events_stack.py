from pathlib import Path

import yaml
from aws_cdk import NestedStack
from aws_cdk.aws_events import EventBus, Rule
from constructs import Construct

from lib import lambdas


class EventsStack(NestedStack):
    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        stack_layers: dict[str, str],
        **kwargs,
    ):
        super().__init__(scope, construct_id, **kwargs)

        bus = EventBus(self, 'LeagueEventBus', event_bus_name='league')

        stack_rules = {}

        with Path.open('./config/event_rules.yaml') as rules_yaml:
            rules_config = yaml.load(rules_yaml, yaml.FullLoader)

            for rule in rules_config['events']:
                new_rule = Rule(
                    self,
                    rule['name'],
                    event_bus=bus,
                    event_pattern={'source': [rule['source']]},
                )

                print(f'TYPE: {type(new_rule)}')

                stack_rules.update({rule['name']: new_rule})

        with Path.open('./config/lambdas/events.yaml') as lambdas_yaml:
            lambdas_config = yaml.load(lambdas_yaml, yaml.FullLoader)

        lambda_bundle = {'layers': stack_layers, 'events': stack_rules}

        for lambda_dict in lambdas_config['lambdas']:
            property_name = lambda_dict['name']
            new_lambda = lambdas.create_lambda(
                self,
                bundle=lambda_bundle,
                **lambda_dict,
            )

            setattr(self, property_name, new_lambda)

        self.league_bus_arn = bus.event_bus_arn
