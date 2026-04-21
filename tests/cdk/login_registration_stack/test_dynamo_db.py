import aws_cdk as core
import aws_cdk.assertions as assertions
import pytest

from league.login_registration_stack import LoginRegistrationStack

app = core.App()
stack = LoginRegistrationStack(app, 'league')
template = assertions.Template.from_stack(stack)


@pytest.mark.cdk
def test_dynamodb_count():

    template.resource_count_is('AWS::DynamoDB::Table', 3)


@pytest.mark.cdk
def test_users_table_props():
    template.has_resource_properties(
        'AWS::DynamoDB::Table',
        {
            'TableName': 'Users',
            'KeySchema': assertions.Match.array_equals(
                [{'AttributeName': 'player_id', 'KeyType': 'HASH'}]
            ),
            'AttributeDefinitions': assertions.Match.array_equals(
                [{'AttributeName': 'player_id', 'AttributeType': 'S'}]
            ),
        },
    )


@pytest.mark.cdk
def test_sessions_table_props():
    template.has_resource_properties(
        'AWS::DynamoDB::Table',
        {
            'TableName': 'Sessions',
            'KeySchema': assertions.Match.array_equals(
                [
                    {'AttributeName': 'player_id', 'KeyType': 'HASH'},
                    {'AttributeName': 'session_id', 'KeyType': 'RANGE'},
                ]
            ),
            'AttributeDefinitions': assertions.Match.array_equals(
                [
                    {'AttributeName': 'player_id', 'AttributeType': 'S'},
                    {'AttributeName': 'session_id', 'AttributeType': 'S'},
                ]
            ),
            'TimeToLiveSpecification': assertions.Match.object_equals(
                {'AttributeName': 'ttl', 'Enabled': True}
            ),
        },
    )


@pytest.mark.cdk
def test_password_reset_table_props():
    template.has_resource_properties(
        'AWS::DynamoDB::Table',
        {
            'TableName': 'PasswordReset',
            'KeySchema': assertions.Match.array_equals(
                [
                    {'AttributeName': 'reset_id', 'KeyType': 'HASH'},
                ]
            ),
            'AttributeDefinitions': assertions.Match.array_equals(
                [
                    {'AttributeName': 'reset_id', 'AttributeType': 'S'},
                ]
            ),
            'TimeToLiveSpecification': assertions.Match.object_equals(
                {'AttributeName': 'ttl', 'Enabled': True}
            ),
        },
    )
