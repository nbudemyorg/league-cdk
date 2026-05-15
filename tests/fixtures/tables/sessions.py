from typing import Any

import boto3
import pytest
from botocore.exceptions import ClientError
from moto import mock_aws
from pytest_mock import MockerFixture
from types_boto3_dynamodb.service_resource import Table


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
def sessions_client_error():
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
    sessions_client_error: dict[str, Any],
):
    """Provide a mocked Dynamodb Sessions table which throws ClientError
    exceptions for GetItem & PutItem"""
    with mock_aws():
        mocker.patch.object(
            sessions_table,
            'put_item',
            side_effect=ClientError(sessions_client_error, 'PutItem'),
        )
        mocker.patch.object(
            sessions_table,
            'get_item',
            side_effect=ClientError(sessions_client_error, 'GetItem'),
        )
        yield sessions_table
