layer_configs = {
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
