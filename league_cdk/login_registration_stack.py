from pathlib import Path

import yaml
from aws_cdk import Fn, Stack
from aws_cdk.aws_lambda import LayerVersion
from constructs import Construct

from lib import ddb, lambdas


class LoginRegistrationStack(Stack):
    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        events_arn: str,
        stack_layers: dict[str, LayerVersion],
        **kwargs,
    ) -> None:
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

        with Path.open('./config/lambdas/login_reg.yaml') as lambdas_yaml:
            lambdas_config = yaml.load(lambdas_yaml, yaml.FullLoader)

        for lambda_dict in lambdas_config['lambdas']:
            property_name = lambda_dict['name']
            new_lambda = lambdas.create_lambda(
                self,
                stack_layers=stack_layers,
                stack_secrets=stack_secrets,
                stack_tables=stack_tables,
                events_arn=events_arn,
                **lambda_dict,
            )

            setattr(self, property_name, new_lambda)
