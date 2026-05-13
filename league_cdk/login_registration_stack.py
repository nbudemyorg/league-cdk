from pathlib import Path

import yaml
from aws_cdk import Fn, Stack
from constructs import Construct

from lib import ddb, lambdas, layers


class LoginRegistrationStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        aws_region = Fn.ref('AWS::Region')
        aws_account = Fn.ref('AWS::AccountId')
        invite_secret_arn = (
            f'arn:aws:secretsmanager:{aws_region}:{aws_account}'
            ':secret:league/invitation_key-*'
        )

        stack_secrets = {}

        new_secret = {'invite': invite_secret_arn}
        stack_secrets.update(new_secret)

        with Path.open('./config/tables.yaml') as tables_yaml:
            tables_config = yaml.load(tables_yaml, yaml.FullLoader)

        stack_tables = {}

        for table_config in tables_config['tables']:
            table_name = table_config['name'].lower()
            new_table = ddb.create_table(self, **table_config)
            stack_tables.update({table_name: new_table})

        with Path.open('./config/layers.yaml') as layers_yaml:
            layers_config = yaml.load(layers_yaml, yaml.FullLoader)

        stack_layers = {}

        for layer in layers_config['layers']:
            new_layer = layers.create_lambda_layer(
                self,
                self.stack_name,
                layer_name=layer['name'],
                layer_source=layer['source'],
            )

            stack_layers.update({layer['name']: new_layer})

        with Path.open('./config/lambdas/login_reg.yaml') as lambdas_yaml:
            lambdas_config = yaml.load(lambdas_yaml, yaml.FullLoader)

        for lambda_dict in lambdas_config['lambdas']:
            property_name = lambda_dict['name']
            new_lambda = lambdas.create_lambda(
                self,
                stack_layers=stack_layers,
                stack_secrets=stack_secrets,
                stack_tables=stack_tables,
                **lambda_dict,
            )

            setattr(self, property_name, new_lambda)
