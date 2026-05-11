import aws_cdk.aws_iam as iam
from aws_cdk import Fn, Stack
from constructs import Construct

from config.lambdas.login_reg import lambda_configs
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

        stack_tables = {}

        users_table = ddb.create_table(self, **ddb_tables['USERS'])

        stack_tables.update({'users': users_table})

        sessions_table = ddb.create_table(self, **ddb_tables['SESSIONS'])

        stack_tables.update({'sessions': sessions_table})

        password_reset_table = ddb.create_table(self, **ddb_tables['RESET'])

        stack_tables.update({'resets': password_reset_table})

        stack_layers = {}

        layer_config = {
            'layers': [
                {
                    'name': 'league',
                    'source': 'layers/league',
                },
                {
                    'name': 'common-pkg',
                    'source': 'layers/pkg/common/requirements.txt',
                },
                {
                    'name': 'bcrypt-pkg',
                    'source': 'layers/pkg/bcrypt/requirements.txt',
                },
                {
                    'name': 'emailvalidator-pkg',
                    'source': './layers/pkg/email/requirements.txt',
                },
            ]
        }

        for layer in layer_config['layers']:
            new_layer = layers.create_lambda_layer(
                self,
                self.stack_name,
                layer_name=layer['name'],
                layer_source=layer['source'],
            )

            stack_layers.update({layer['name']: new_layer})

        reg_get_config = lambda_configs.get('reg_get')

        registration_lambda_get = lambdas.create_lambda(
            self, stack_layers=stack_layers, **reg_get_config
        )

        reg_post_config = lambda_configs.get('reg_post')

        registration_lambda_post = lambdas.create_lambda(
            self,
            stack_layers=stack_layers,
            stack_tables=stack_tables,
            **reg_post_config,
        )

        registration_invite_ro = iam.PolicyStatement(
            effect=iam.Effect.ALLOW,
            actions=['secretsmanager:GetSecretValue'],
            resources=[invite_secret_arn],
            sid='RegistrationLambdaInviteSecretRO',
        )

        registration_lambda_post.add_to_role_policy(registration_invite_ro)

        login_get_config = lambda_configs.get('login_get')

        login_lambda_get = lambdas.create_lambda(
            self, stack_layers=stack_layers, **login_get_config
        )

        login_post_config = lambda_configs.get('login_post')

        login_lambda_post = lambdas.create_lambda(
            self,
            stack_layers=stack_layers,
            stack_tables=stack_tables,
            **login_post_config,
        )

        home_get_config = lambda_configs.get('home_get')

        home_page_lambda_get = lambdas.create_lambda(
            self,
            stack_layers=stack_layers,
            stack_tables=stack_tables,
            **home_get_config,
        )

        reset_get_config = lambda_configs.get('reset_get')

        password_reset_lambda_get = lambdas.create_lambda(
            self, stack_layers, **reset_get_config
        )

        reset_post_config = lambda_configs.get('reset_post')

        password_reset_lambda_post = lambdas.create_lambda(
            self,
            stack_layers=stack_layers,
            stack_tables=stack_tables,
            **reset_post_config,
        )

        reset_id_get_config = lambda_configs.get('reset_id_get')

        password_reset_id_lambda_get = lambdas.create_lambda(
            self,
            stack_layers=stack_layers,
            stack_tables=stack_tables,
            **reset_id_get_config,
        )

        reset_id_post_config = lambda_configs.get('reset_id_post')

        password_reset_id_lambda_post = lambdas.create_lambda(
            self,
            stack_layers=stack_layers,
            stack_tables=stack_tables,
            **reset_id_post_config,
        )

        self.login_lambda = login_lambda_post
        self.login_lambda_get = login_lambda_get
        self.registration_lambda = registration_lambda_post
        self.registration_lambda_get = registration_lambda_get
        self.home_page_lambda = home_page_lambda_get
        self.password_reset_lambda_get = password_reset_lambda_get
        self.password_reset_lambda_post = password_reset_lambda_post
        self.password_reset_id_lambda_get = password_reset_id_lambda_get
        self.password_reset_id_lambda_post = password_reset_id_lambda_post
