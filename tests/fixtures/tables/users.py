from typing import Any

import boto3
import pytest
from botocore.exceptions import ClientError
from moto import mock_aws
from pytest_mock import MockerFixture
from types_boto3_dynamodb.service_resource import Table


@pytest.fixture(scope='function')
def users_table(aws_credentials):
    """Provide a mocked Dynamodb Users table"""
    with mock_aws():
        dynamodb = boto3.resource('dynamodb')
        users_table = dynamodb.create_table(
            TableName='Users',
            BillingMode='PAY_PER_REQUEST',
            AttributeDefinitions=[
                {'AttributeName': 'player_id', 'AttributeType': 'S'}
            ],
            KeySchema=[{'AttributeName': 'player_id', 'KeyType': 'HASH'}],
        )
        yield users_table


@pytest.fixture
def test_user(scope='function'):
    """Test user of type UserItem"""
    user_data = {
        'player_id': 'PlayerOne',
        'password': 'NotReallyAHash',
        'email': 'bob@hotmail.com',
    }
    yield user_data


@pytest.fixture(scope='function')
def users_table_with_user(users_table: Table, test_user: dict[str, str]):
    """Users table with a user item"""
    users_table.put_item(Item=test_user)
    yield users_table


@pytest.fixture(scope='function')
def users_client_error():
    yield {
        'Error': {
            'Code': 'PyTestSimulatedException',
            'Message': 'Pytest mocked ClientError Users Table',
        }
    }


@pytest.fixture(scope='function')
def users_table_client_error(
    users_table: Table,
    mocker: MockerFixture,
    users_client_error: dict[str, Any],
):
    """Provide a mocked Dynamodb Users table which throws ClientError
    exceptions for GetItem & PutItem"""
    with mock_aws():
        mocker.patch.object(
            users_table,
            'put_item',
            side_effect=ClientError(users_client_error, 'PutItem'),
        )
        mocker.patch.object(
            users_table,
            'get_item',
            side_effect=ClientError(users_client_error, 'GetItem'),
        )
        mocker.patch.object(
            users_table,
            'update_item',
            side_effect=ClientError(users_client_error, 'UpdateItem'),
        )
        yield users_table