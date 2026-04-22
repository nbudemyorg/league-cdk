import aws_cdk as core
import aws_cdk.assertions as assertions

from league.login_registration_stack import LoginRegistrationStack

app = core.App()
stack = LoginRegistrationStack(app, 'league')
template = assertions.Template.from_stack(stack)


def test_lambda_count():
    template.resource_count_is('AWS::Lambda::Function', 7)


def test_lambda_layer_count():
    template.resource_count_is('AWS::Lambda::LayerVersion', 5)


def test_registration_get_lambda():
    template.has_resource_properties(
        'AWS::Lambda::Function',
        {
            'Handler': 'register_get.lambda_handler',
            'FunctionName': 'UserRegistrationGET',
            'Runtime': 'python3.14',
            'Timeout': 5,
        },
    )


def test_registration_post_lambda():
    template.has_resource_properties(
        'AWS::Lambda::Function',
        {
            'Handler': 'register_post.lambda_handler',
            'FunctionName': 'UserRegistrationPOST',
            'Runtime': 'python3.14',
            'Timeout': 10,
        },
    )


def test_registration_post_lambda_role_policies():

    template.has_resource_properties(
        'AWS::IAM::Policy',
        {
            'PolicyDocument': assertions.Match.object_like(
                {
                    'Statement': assertions.Match.array_with(
                        [
                            assertions.Match.object_like(
                                {
                                    'Action': [
                                        'dynamodb:PutItem',
                                        'dynamodb:GetItem',
                                    ],
                                    'Effect': 'Allow',
                                    'Resource': {
                                        'Fn::GetAtt': assertions.Match.array_with(
                                            [
                                                assertions.Match.string_like_regexp(
                                                    '(Users).{8}$'
                                                ),
                                                'Arn',
                                            ]
                                        )
                                    },
                                    'Sid': 'RegistrationLambdaUsersTableRW',
                                }
                            ),
                            assertions.Match.object_like(
                                {
                                    'Action': 'dynamodb:PutItem',
                                    'Effect': 'Allow',
                                    'Resource': {
                                        'Fn::GetAtt': assertions.Match.array_with(
                                            [
                                                assertions.Match.string_like_regexp(
                                                    '(Sessions).{8}$'
                                                ),
                                                'Arn',
                                            ]
                                        )
                                    },
                                    'Sid': 'RegistrationLambdaSessionsTableWO',
                                }
                            ),
                            assertions.Match.object_like(
                                {
                                    'Action': 'secretsmanager:GetSecretValue',
                                    'Effect': 'Allow',
                                    'Resource': {
                                        'Fn::Join': assertions.Match.array_with(
                                            [
                                                assertions.Match.array_with(
                                                    [
                                                        'arn:aws:secretsmanager:',
                                                        ':secret:league/invitation_key-*',
                                                    ]
                                                )
                                            ]
                                        )
                                    },
                                    'Sid': 'RegistrationLambdaInviteSecretRO',
                                }
                            ),
                        ]
                    )
                }
            )
        },
    )


def test_home_page_lambda():
    template.has_resource_properties(
        'AWS::Lambda::Function',
        {
            'Handler': 'home_get.lambda_handler',
            'FunctionName': 'HomePageGET',
            'Runtime': 'python3.14',
            'Timeout': 5,
        },
    )


def test_home_page_lambda_role_policies():
    template.has_resource_properties(
        'AWS::IAM::Policy',
        {
            'PolicyDocument': assertions.Match.object_like(
                {
                    'Statement': assertions.Match.array_with(
                        [
                            assertions.Match.object_like(
                                {
                                    'Action': 'dynamodb:GetItem',
                                    'Effect': 'Allow',
                                    'Resource': {
                                        'Fn::GetAtt': assertions.Match.array_with(
                                            [
                                                assertions.Match.string_like_regexp(
                                                    '(Sessions).{8}$'
                                                ),
                                                'Arn',
                                            ]
                                        )
                                    },
                                    'Sid': 'HomeLambdaSessionsTableRO',
                                }
                            )
                        ]
                    )
                }
            )
        },
    )


def test_user_login_get_lambda():
    template.has_resource_properties(
        'AWS::Lambda::Function',
        {
            'Handler': 'login_get.lambda_handler',
            'FunctionName': 'UserLoginGET',
            'Runtime': 'python3.14',
            'Timeout': 5,
        },
    )


def test_user_login_post_lambda():
    template.has_resource_properties(
        'AWS::Lambda::Function',
        {
            'Handler': 'login_post.lambda_handler',
            'FunctionName': 'UserLoginPOST',
            'Runtime': 'python3.14',
            'Timeout': 5,
        },
    )


def test_login_lambda_role_policies():
    template.has_resource_properties(
        'AWS::IAM::Policy',
        {
            'PolicyDocument': assertions.Match.object_like(
                {
                    'Statement': assertions.Match.array_with(
                        [
                            assertions.Match.object_like(
                                {
                                    'Action': 'dynamodb:GetItem',
                                    'Effect': 'Allow',
                                    'Resource': {
                                        'Fn::GetAtt': assertions.Match.array_with(
                                            [
                                                assertions.Match.string_like_regexp(
                                                    '(Users).{8}$'
                                                ),
                                                'Arn',
                                            ]
                                        )
                                    },
                                    'Sid': 'LoginLambdaUsersTableRO',
                                }
                            ),
                            assertions.Match.object_like(
                                {
                                    'Action': 'dynamodb:PutItem',
                                    'Effect': 'Allow',
                                    'Resource': {
                                        'Fn::GetAtt': assertions.Match.array_with(
                                            [
                                                assertions.Match.string_like_regexp(
                                                    '(Sessions).{8}$'
                                                ),
                                                'Arn',
                                            ]
                                        )
                                    },
                                    'Sid': 'LoginLambdaSessionsTableWO',
                                }
                            ),
                        ]
                    )
                }
            )
        },
    )
