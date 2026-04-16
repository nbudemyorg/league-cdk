import os
import sys
from unittest.mock import MagicMock

import boto3
import pytest
from botocore.exceptions import ClientError
from moto import mock_aws
from pytest_mock import MockerFixture
from types_boto3_dynamodb.service_resource import Table


@pytest.fixture(scope='module')
def mock_html_layer():
    sys.modules['html_layer'] = MagicMock()
    sys.modules['html_layer']['home_page'] = MagicMock()
    sys.modules['html_layer']['access_denied'] = MagicMock()
    sys.modules['html_layer']['server_error'] = MagicMock()
    sys.modules['html_layer']['login_form'] = MagicMock()
    sys.modules['html_layer']['registration_form'] = MagicMock()


@pytest.fixture(scope='module')
def mock_auth_layer():
    sys.modules['auth_layer'] = MagicMock()
    sys.modules['auth_layer']['valid_session'] = MagicMock()
    sys.modules['auth_layer']['create_session_item'] = MagicMock()
    sys.modules['auth_layer']['valid_player_id'] = MagicMock()
    sys.modules['auth_layer']['valid_psn_id'] = MagicMock()
    sys.modules['auth_layer']['valid_xbox_id'] = MagicMock()


@pytest.fixture(scope='module')
def mock_bcrypt_module():
    sys.modules['bcrypt'] = MagicMock()


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


@pytest.fixture(scope='function')
def users_table_client_error(users_table: Table, mocker: MockerFixture):
    """Provide a mocked Dynamodb Users table which throws ClientError
    exceptions for GetItem & PutItem"""
    with mock_aws():
        error_object = {
            'Error': {
                'Code': 'PyTestSimulatedException',
                'Message': 'Pytest mocked ClientError',
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


@pytest.fixture
def test_user(scope='function'):
    user_data = {'player_id': 'PlayerOne', 'password': 'NotReallyAHash'}
    yield user_data


@pytest.fixture(scope='function')
def users_table_with_user(users_table: Table, test_user: dict[str, str]):
    users_table.put_item(Item=test_user)
    yield users_table


@pytest.fixture(scope='function')
def invitation_secret(aws_credentials):
    """Provide Secrets Manager client with a predefined invitation secret"""
    with mock_aws():
        sm_client = boto3.client(
            service_name='secretsmanager', region_name='eu-west-1'
        )
        sm_client.create_secret(
            Name='league/invitation_key', SecretString='CorrectValue'
        )
        yield sm_client
