import aws_cdk.aws_dynamodb as dynamodb
import aws_cdk.aws_iam as iam
from aws_cdk import Duration, Fn, RemovalPolicy, Stack
from aws_cdk.aws_lambda import Code, Function, Runtime
from constructs import Construct

from lib import layers


class LoginRegistrationStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        aws_region = Fn.ref('AWS::Region')
        aws_account = Fn.ref('AWS::AccountId')
        invite_secret_arn = (
            f'arn:aws:secretsmanager:{aws_region}:{aws_account}'
            ':secret:league/invitation_key-*'
        )

        users_table = dynamodb.Table(
            self,
            'Users',
            removal_policy=RemovalPolicy.DESTROY,
            table_name='Users',
            billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST,
            partition_key=dynamodb.Attribute(
                name='player_id', type=dynamodb.AttributeType.STRING
            ),
        )

        sessions_table = dynamodb.Table(
            self,
            'Sessions',
            removal_policy=RemovalPolicy.DESTROY,
            table_name='Sessions',
            billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST,
            partition_key=dynamodb.Attribute(
                name='player_id', type=dynamodb.AttributeType.STRING
            ),
            sort_key=dynamodb.Attribute(
                name='session_id', type=dynamodb.AttributeType.STRING
            ),
            time_to_live_attribute='ttl',
        )

        password_reset_table = dynamodb.Table(
            self,
            'PasswordReset',
            removal_policy=RemovalPolicy.DESTROY,
            table_name='PasswordReset',
            billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST,
            partition_key=dynamodb.Attribute(
                name='reset_id', type=dynamodb.AttributeType.STRING
            ),
            time_to_live_attribute='ttl',
        )

        common_pkg_layer = layers.create_lambda_layer(
            self,
            self.stack_name,
            layer_name='common-pkg',
            layer_source='layers/pkg/common/requirements.txt',
        )

        static_content_layer = layers.create_lambda_layer(
            self,
            self.stack_name,
            layer_name='static-content',
            layer_source='layers/static',
        )

        bcrypt_pkg_layer = layers.create_lambda_layer(
            self,
            self.stack_name,
            layer_name='bcrypt',
            layer_source='layers/pkg/bcrypt/requirements.txt',
        )

        sessions_dependencies_layer = layers.create_lambda_layer(
            self,
            self.stack_name,
            layer_name='sessions',
            layer_source='./layers/sessions',
        )

        registration_lambda_get = Function(
            self,
            'UserRegistrationGET',
            function_name='UserRegistrationGET',
            handler='register_get.lambda_handler',
            runtime=Runtime.PYTHON_3_14,
            code=Code.from_asset(path='src/user_registration/get'),
            timeout=Duration.seconds(5),
            layers=[static_content_layer, common_pkg_layer],
        )

        registration_lambda_post = Function(
            self,
            'UserRegistrationPOST',
            function_name='UserRegistrationPOST',
            handler='register_post.lambda_handler',
            runtime=Runtime.PYTHON_3_14,
            code=Code.from_asset(path='src/user_registration/post'),
            timeout=Duration.seconds(10),
            layers=[
                bcrypt_pkg_layer,
                sessions_dependencies_layer,
                common_pkg_layer,
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
            layers=[static_content_layer, common_pkg_layer],
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
                sessions_dependencies_layer,
                common_pkg_layer,
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
                sessions_dependencies_layer,
                static_content_layer,
                common_pkg_layer,
            ],
        )

        home_sessions_ro = iam.PolicyStatement(
            effect=iam.Effect.ALLOW,
            actions=['dynamodb:GetItem'],
            resources=[sessions_table.table_arn],
            sid='HomeLambdaSessionsTableRO',
        )

        home_page_lambda_get.add_to_role_policy(home_sessions_ro)

        self.login_lambda = login_lambda_post
        self.login_lambda_get = login_lambda_get
        self.registration_lambda = registration_lambda_post
        self.registration_lambda_get = registration_lambda_get
        self.home_page_lambda = home_page_lambda_get
