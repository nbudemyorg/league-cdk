from typing import Any

import boto3
import pytest
from botocore.exceptions import ClientError
from moto import mock_aws
from pytest_mock import MockerFixture
from types_boto3_dynamodb.service_resource import Table


@pytest.fixture(scope='function')
def reset_item():
    yield {'reset_id': 'BasicTestString', 'player_id': 'PlayerOne'}


@pytest.fixture(scope='function')
def reset_table(aws_credentials):
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
def reset_table_with_item(reset_table: Table, reset_item: dict[str, Any]):
    reset_table.put_item(Item=reset_item)
    yield reset_table


@pytest.fixture(scope='function')
def reset_client_error():
    yield {
        'Error': {
            'Code': 'PyTestSimulatedException',
            'Message': 'Pytest mocked ClientError PasswordReset Table',
        }
    }


@pytest.fixture(scope='function')
def reset_table_client_error(
    reset_table: Table,
    reset_client_error: ClientError,
    mocker: MockerFixture,
):
    """Provide a mocked Dynamodb PasswordReset table which throws ClientError
    exceptions for GetItem & PutItem"""
    with mock_aws():
        mocker.patch.object(
            reset_table,
            'put_item',
            side_effect=ClientError(reset_client_error, 'PutItem'),
        )
        mocker.patch.object(
            reset_table,
            'get_item',
            side_effect=ClientError(reset_client_error, 'GetItem'),
        )
        yield reset_table
