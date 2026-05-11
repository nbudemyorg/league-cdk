lambda_configs = {
    'reg_get': {
        'lambda_name': 'UserRegistrationGET',
        'handler': 'register_get.lambda_handler',
        'source_dir': 'src/user_registration/get',
        'layers': ['league', 'common-pkg'],
    },
    'reg_post': {
        'lambda_name': 'UserRegistrationPOST',
        'handler': 'register_post.lambda_handler',
        'source_dir': 'src/user_registration/post',
        'timeout': 10,
        'layers': [
            'bcrypt-pkg',
            'common-pkg',
            'emailvalidator-pkg',
            'league',
        ],
        'environment': {
            'INVITE_KEY': 'league/invitation_key',
            'REGION': 'eu-west-1',
        },
        'policies': {
            'tables': [
                {
                    'name': 'users',
                    'actions': ['dynamodb:PutItem', 'dynamodb:GetItem'],
                },
                {'name': 'sessions', 'actions': ['dynamodb:PutItem']},
            ]
        },
    },
    'login_get': {
        'lambda_name': 'UserLoginGET',
        'handler': 'login_get.lambda_handler',
        'source_dir': 'src/user_login/get',
        'layers': ['league', 'common-pkg'],
    },
    'login_post': {
        'lambda_name': 'UserLoginPOST',
        'handler': 'login_post.lambda_handler',
        'source_dir': 'src/user_login/post',
        'layers': ['bcrypt-pkg', 'league', 'common-pkg'],
        'policies': {
            'tables': [
                {
                    'name': 'users',
                    'actions': ['dynamodb:GetItem'],
                },
                {'name': 'sessions', 'actions': ['dynamodb:PutItem']},
            ]
        },
    },
    'home_get': {
        'lambda_name': 'HomePageGET',
        'handler': 'home_get.lambda_handler',
        'source_dir': 'src/home_page/get',
        'layers': ['common-pkg', 'league'],
        'policies': {
            'tables': [
                {
                    'name': 'sessions',
                    'actions': ['dynamodb:GetItem'],
                },
            ]
        },
    },
    'reset_get': {
        'lambda_name': 'UserPasswordResetGET',
        'handler': 'reset_get.lambda_handler',
        'source_dir': 'src/password_reset/get',
        'layers': ['common-pkg', 'league'],
    },
    'reset_post': {
        'lambda_name': 'UserPasswordResetPOST',
        'handler': 'reset_post.lambda_handler',
        'source_dir': 'src/password_reset/post',
        'timeout': 10,
        'layers': ['common-pkg', 'league'],
        'policies': {
            'tables': [
                {
                    'name': 'users',
                    'actions': [
                        'dynamodb:PutItem',
                        'dynamodb:GetItem',
                        'dynamodb:UpdateItem',
                    ],
                },
                {'name': 'resets', 'actions': ['dynamodb:PutItem']},
            ]
        },
    },
    'reset_id_get': {
        'lambda_name': 'UserPasswordResetIdGET',
        'handler': 'reset_id_get.lambda_handler',
        'source_dir': 'src/password_reset/id/get',
        'layers': ['common-pkg', 'league'],
        'policies': {
            'tables': [
                {
                    'name': 'resets',
                    'actions': ['dynamodb:GetItem'],
                },
            ]
        },
    },
    'reset_id_post': {
        'lambda_name': 'UserPasswordResetIdPOST',
        'handler': 'reset_id_post.lambda_handler',
        'source_dir': 'src/password_reset/id/post',
        'layers': ['bcrypt-pkg', 'common-pkg', 'league'],
        'policies': {
            'tables': [
                {
                    'name': 'resets',
                    'actions': [
                        'dynamodb:GetItem',
                        'dynamodb:PutItem',
                        'dynamodb:DeleteItem',
                    ],
                },
                {
                    'name': 'users',
                    'actions': [
                        'dynamodb:PutItem',
                        'dynamodb:GetItem',
                        'dynamodb:UpdateItem',
                    ],
                },
            ]
        },
    },
}
