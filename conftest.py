import os
import sys
from datetime import UTC, datetime
from typing import Any
from unittest.mock import MagicMock

import boto3
import pytest
from botocore.exceptions import ClientError
from moto import mock_aws
from pytest_mock import MockerFixture
from types_boto3_dynamodb.service_resource import Table


@pytest.fixture(scope='module')
def mock_html_layer():
    sys.modules['league.static.pages'] = MagicMock()
    sys.modules['league.templates'] = MagicMock()


@pytest.fixture(scope='module')
def mock_sessions_layer():
    sys.modules['league.auth'] = MagicMock()
    sys.modules['league.credentials'] = MagicMock()
    sys.modules['league.aws_secrets'] = MagicMock()
    sys.modules['league.validate'] = MagicMock()


@pytest.fixture(scope='module')
def mock_bcrypt_module():
    sys.modules['bcrypt'] = MagicMock()


@pytest.fixture(scope='module')
def mock_league_tables_layer():
    sys.modules['league.tables.item.types'] = MagicMock()
    sys.modules['league.tables.item.libs'] = MagicMock()
    sys.modules['league.tables.password_reset'] = MagicMock()
    sys.modules['league.tables.response.libs'] = MagicMock()
    sys.modules['league.tables.response.types'] = MagicMock()
    sys.modules['league.tables.sessions'] = MagicMock()
    sys.modules['league.tables.users'] = MagicMock()


@pytest.fixture(scope='function')
def aws_credentials():
    """Mocked AWS Credentials for moto."""
    os.environ['AWS_ACCESS_KEY_ID'] = 'testing'
    os.environ['AWS_SECRET_ACCESS_KEY'] = 'testing'
    os.environ['AWS_SECURITY_TOKEN'] = 'testing'
    os.environ['AWS_SESSION_TOKEN'] = 'testing'
    os.environ['AWS_DEFAULT_REGION'] = 'us-east-1'


@pytest.fixture(scope='function')
def session_item(mock_uuid):
    """Provide a session item for the Sessions table"""
    mocked_uuid_response = '12345678-1234-4678-8234-567812345678'
    mock_uuid.uuid4.set(mocked_uuid_response)
    player_id = 'PlayerOne'

    item = {'player_id': player_id, 'session_id': mocked_uuid_response}

    yield item


@pytest.fixture(scope='function')
def sessions_table(aws_credentials):
    """Provide a mocked Dynamodb Sessions table"""
    with mock_aws():
        dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
        # Create a sample table
        sessions_table = dynamodb.create_table(
            TableName='Sessions',
            BillingMode='PAY_PER_REQUEST',
            AttributeDefinitions=[
                {'AttributeName': 'player_id', 'AttributeType': 'S'},
                {'AttributeName': 'session_id', 'AttributeType': 'S'},
            ],
            KeySchema=[
                {'AttributeName': 'player_id', 'KeyType': 'HASH'},
                {'AttributeName': 'session_id', 'KeyType': 'RANGE'},
            ],
        )
        yield sessions_table


@pytest.fixture(scope='function')
def sessions_table_with_session(
    sessions_table: Table, session_item: dict[str, str]
):
    """Sessions table with a session item"""
    sessions_table.put_item(Item=session_item)
    yield sessions_table


@pytest.fixture(scope='function')
def client_error_object():
    yield {
        'Error': {
            'Code': 'PyTestSimulatedException',
            'Message': 'Pytest mocked ClientError Sessions Table',
        }
    }


@pytest.fixture(scope='function')
def sessions_table_client_error(
    sessions_table: Table,
    mocker: MockerFixture,
    client_error_object: dict[str, Any],
):
    """Provide a mocked Dynamodb Sessions table which throws ClientError
    exceptions for GetItem & PutItem"""
    with mock_aws():
        mocker.patch.object(
            sessions_table,
            'put_item',
            side_effect=ClientError(client_error_object, 'PutItem'),
        )
        mocker.patch.object(
            sessions_table,
            'get_item',
            side_effect=ClientError(error_object, 'GetItem'),
        )
        yield


@pytest.fixture(scope='function')
def frozen_date():
    yield datetime(
        year=2026,
        month=4,
        day=20,
        hour=15,
        minute=6,
        second=3,
        microsecond=100,
        tzinfo=UTC,
    )


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
def users_table_client_error(users_table: Table, mocker: MockerFixture):
    """Provide a mocked Dynamodb Users table which throws ClientError
    exceptions for GetItem & PutItem"""
    with mock_aws():
        error_object = {
            'Error': {
                'Code': 'PyTestSimulatedException',
                'Message': 'Pytest mocked ClientError Users Table',
            }
        }
        mocker.patch.object(
            users_table,
            'put_item',
            side_effect=ClientError(error_object, 'PutItem'),
        )
        mocker.patch.object(
            users_table,
            'get_item',
            side_effect=ClientError(error_object, 'GetItem'),
        )
        yield users_table


@pytest.fixture(scope='function')
def password_reset_table(aws_credentials):
    """Provide a mocked Dynamodb PasswordReset table"""
    with mock_aws():
        dynamodb = boto3.resource('dynamodb')
        password_reset_table = dynamodb.create_table(
            TableName='PasswordReset',
            BillingMode='PAY_PER_REQUEST',
            AttributeDefinitions=[
                {'AttributeName': 'reset_id', 'AttributeType': 'S'}
            ],
            KeySchema=[{'AttributeName': 'reset_id', 'KeyType': 'HASH'}],
        )
        yield password_reset_table


@pytest.fixture(scope='function')
def password_reset_table_client_error(
    password_reset_table: Table, mocker: MockerFixture
):
    """Provide a mocked Dynamodb PasswordReset table which throws ClientError
    exceptions for GetItem & PutItem"""
    with mock_aws():
        error_object = {
            'Error': {
                'Code': 'PyTestSimulatedException',
                'Message': 'Pytest mocked ClientError PasswordReset Table',
            }
        }
        mocker.patch.object(
            password_reset_table,
            'put_item',
            side_effect=ClientError(error_object, 'PutItem'),
        )
        mocker.patch.object(
            password_reset_table,
            'get_item',
            side_effect=ClientError(error_object, 'GetItem'),
        )
        yield password_reset_table
