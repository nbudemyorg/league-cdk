import aws_cdk.aws_iam as iam
from aws_cdk import Duration, Fn, Stack
from aws_cdk.aws_lambda import Code, Function, Runtime
from constructs import Construct

from config.tables import ddb_tables
from lib import ddb, layers


class LoginRegistrationStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        aws_region = Fn.ref('AWS::Region')
        aws_account = Fn.ref('AWS::AccountId')
        invite_secret_arn = (
            f'arn:aws:secretsmanager:{aws_region}:{aws_account}'
            ':secret:league/invitation_key-*'
        )

        users_table = ddb.create_table(self, **ddb_tables['USERS'])

        sessions_table = ddb.create_table(self, **ddb_tables['SESSIONS'])

        password_reset_table = ddb.create_table(self, **ddb_tables['RESET'])

        league_layer = layers.create_lambda_layer(
            self,
            self.stack_name,
            layer_name='league_layer',
            layer_source='layers/league',
        )

        common_pkg_layer = layers.create_lambda_layer(
            self,
            self.stack_name,
            layer_name='common-pkg',
            layer_source='layers/pkg/common/requirements.txt',
        )

        bcrypt_pkg_layer = layers.create_lambda_layer(
            self,
            self.stack_name,
            layer_name='bcrypt',
            layer_source='layers/pkg/bcrypt/requirements.txt',
        )

        email_validator_layer = layers.create_lambda_layer(
            self,
            self.stack_name,
            layer_name='emailvalidator',
            layer_source='./layers/pkg/email/requirements.txt',
        )

        registration_lambda_get = Function(
            self,
            'UserRegistrationGET',
            function_name='UserRegistrationGET',
            handler='register_get.lambda_handler',
            runtime=Runtime.PYTHON_3_14,
            code=Code.from_asset(path='src/user_registration/get'),
            timeout=Duration.seconds(5),
            layers=[league_layer, common_pkg_layer],
        )

        registration_lambda_post = Function(
            self,
            'UserRegistrationPOST',
            function_name='UserRegistrationPOST',
            handler='register_post.lambda_handler',
            runtime=Runtime.PYTHON_3_14,
            code=Code.from_asset(path='src/user_registration/post'),
            timeout=Duration.seconds(10),
            environment={
                'INVITE_KEY': 'league/invitation_key',
                'REGION': 'eu-west-1',
            },
            layers=[
                bcrypt_pkg_layer,
                common_pkg_layer,
                email_validator_layer,
                league_layer,
            ],
        )

        registration_users_rw = iam.PolicyStatement(
            effect=iam.Effect.ALLOW,
            actions=['dynamodb:PutItem', 'dynamodb:GetItem'],
            resources=[users_table.table_arn],
            sid='RegistrationLambdaUsersTableRW',
        )

        registration_sessions_wo = iam.PolicyStatement(
            effect=iam.Effect.ALLOW,
            actions=['dynamodb:PutItem'],
            resources=[sessions_table.table_arn],
            sid='RegistrationLambdaSessionsTableWO',
        )

        registration_invite_ro = iam.PolicyStatement(
            effect=iam.Effect.ALLOW,
            actions=['secretsmanager:GetSecretValue'],
            resources=[invite_secret_arn],
            sid='RegistrationLambdaInviteSecretRO',
        )

        registration_lambda_post.add_to_role_policy(registration_users_rw)
        registration_lambda_post.add_to_role_policy(registration_sessions_wo)
        registration_lambda_post.add_to_role_policy(registration_invite_ro)

        login_lambda_get = Function(
            self,
            'UserLoginGET',
            function_name='UserLoginGET',
            handler='login_get.lambda_handler',
            runtime=Runtime.PYTHON_3_14,
            code=Code.from_asset(path='src/user_login/get'),
            timeout=Duration.seconds(5),
            layers=[league_layer, common_pkg_layer],
        )

        login_lambda_post = Function(
            self,
            'UserLoginPOST',
            function_name='UserLoginPOST',
            handler='login_post.lambda_handler',
            runtime=Runtime.PYTHON_3_14,
            code=Code.from_asset(path='src/user_login/post'),
            timeout=Duration.seconds(5),
            layers=[
                bcrypt_pkg_layer,
                common_pkg_layer,
                league_layer,
            ],
        )

        login_users_ro = iam.PolicyStatement(
            effect=iam.Effect.ALLOW,
            actions=['dynamodb:GetItem'],
            resources=[users_table.table_arn],
            sid='LoginLambdaUsersTableRO',
        )

        login_session_wo = iam.PolicyStatement(
            effect=iam.Effect.ALLOW,
            actions=['dynamodb:PutItem'],
            resources=[sessions_table.table_arn],
            sid='LoginLambdaSessionsTableWO',
        )

        login_lambda_post.add_to_role_policy(login_users_ro)
        login_lambda_post.add_to_role_policy(login_session_wo)

        home_page_lambda_get = Function(
            self,
            'HomePage',
            function_name='HomePageGET',
            handler='home_get.lambda_handler',
            runtime=Runtime.PYTHON_3_14,
            code=Code.from_asset(path='src/home_page/get'),
            timeout=Duration.seconds(5),
            layers=[
                common_pkg_layer,
                league_layer,
            ],
        )

        home_sessions_ro = iam.PolicyStatement(
            effect=iam.Effect.ALLOW,
            actions=['dynamodb:GetItem'],
            resources=[sessions_table.table_arn],
            sid='HomeLambdaSessionsTableRO',
        )

        home_page_lambda_get.add_to_role_policy(home_sessions_ro)

        password_reset_lambda_get = Function(
            self,
            'UserPasswordResetGET',
            function_name='UserPasswordResetGET',
            handler='reset_get.lambda_handler',
            runtime=Runtime.PYTHON_3_14,
            code=Code.from_asset(path='src/password_reset/get'),
            timeout=Duration.seconds(5),
            layers=[
                common_pkg_layer,
                league_layer,
            ],
        )

        password_reset_lambda_post = Function(
            self,
            'UserPasswordResetPOST',
            function_name='UserPasswordResetPOST',
            handler='reset_post.lambda_handler',
            runtime=Runtime.PYTHON_3_14,
            code=Code.from_asset(path='src/password_reset/post'),
            timeout=Duration.seconds(10),
            layers=[
                common_pkg_layer,
                league_layer,
            ],
        )

        password_reset_users_rw = iam.PolicyStatement(
            effect=iam.Effect.ALLOW,
            actions=[
                'dynamodb:PutItem',
                'dynamodb:GetItem',
                'dynamodb:UpdateItem',
            ],
            resources=[users_table.table_arn],
            sid='PasswordResetLambdaUsersTableRW',
        )

        password_reset_table_wo = iam.PolicyStatement(
            effect=iam.Effect.ALLOW,
            actions=['dynamodb:PutItem'],
            resources=[password_reset_table.table_arn],
            sid='PasswordResetLambdaPasswordResetTableRW',
        )

        password_reset_table_ro = iam.PolicyStatement(
            effect=iam.Effect.ALLOW,
            actions=['dynamodb:GetItem'],
            resources=[password_reset_table.table_arn],
            sid='PasswordResetLambdaPasswordResetTableRO',
        )

        password_reset_table_rw = iam.PolicyStatement(
            effect=iam.Effect.ALLOW,
            actions=[
                'dynamodb:GetItem',
                'dynamodb:PutItem',
                'dynamodb:DeleteItem',
            ],
            resources=[password_reset_table.table_arn],
            sid='PasswordResetLambdaPasswordResetTableRW',
        )

        password_reset_lambda_post.add_to_role_policy(password_reset_users_rw)
        password_reset_lambda_post.add_to_role_policy(password_reset_table_wo)

        password_reset_id_lambda_get = Function(
            self,
            'UserPasswordResetIdGET',
            function_name='UserPasswordResetIdGET',
            handler='reset_id_get.lambda_handler',
            runtime=Runtime.PYTHON_3_14,
            code=Code.from_asset(path='src/password_reset/id/get'),
            timeout=Duration.seconds(5),
            layers=[
                common_pkg_layer,
                league_layer,
            ],
        )

        password_reset_id_lambda_get.add_to_role_policy(
            password_reset_table_ro
        )

        password_reset_id_lambda_post = Function(
            self,
            'UserPasswordResetIdPOST',
            function_name='UserPasswordResetIdPOST',
            handler='reset_id_post.lambda_handler',
            runtime=Runtime.PYTHON_3_14,
            code=Code.from_asset(path='src/password_reset/id/post'),
            timeout=Duration.seconds(5),
            layers=[
                bcrypt_pkg_layer,
                common_pkg_layer,
                league_layer,
            ],
        )

        password_reset_id_lambda_post.add_to_role_policy(
            password_reset_table_rw
        )
        password_reset_id_lambda_post.add_to_role_policy(
            password_reset_users_rw
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
