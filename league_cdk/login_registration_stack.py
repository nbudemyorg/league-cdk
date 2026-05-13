from aws_cdk import Fn, Stack
from constructs import Construct

from config.lambdas.login_reg import lambda_configs
from config.layers import layer_configs
from config.tables import ddb_tables
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

        stack_tables = {}

        for table_config in ddb_tables['tables']:
            table_name = table_config['table_name'].lower()
            new_table = ddb.create_table(self, **table_config)
            stack_tables.update({table_name: new_table})

        stack_layers = {}

        for layer in layer_configs['layers']:
            new_layer = layers.create_lambda_layer(
                self,
                self.stack_name,
                layer_name=layer['name'],
                layer_source=layer['source'],
            )

            stack_layers.update({layer['name']: new_layer})

        for lambda_dict in lambda_configs['lambdas']:
            property_name = str(list(lambda_dict.keys())[0])
            lambda_config = lambda_dict[property_name]
            new_lambda = lambdas.create_lambda(
                self,
                stack_layers=stack_layers,
                stack_secrets=stack_secrets,
                stack_tables=stack_tables,
                **lambda_config,
            )

            setattr(self, property_name, new_lambda)
