import re
import sys

import pytest
from botocore.exceptions import ClientError
from pytest_mock import MockFixture
from types_boto3_dynamodb.service_resource import Table

from layers.tables.python.league.tables.item.types import ResetItem


@pytest.mark.reset_table
def test_mocked_modules(mock_league_tables_layer: None) -> None:
    """Import mocked modules for subsequent tests"""
    assert 'league.tables.item.libs' in sys.modules
    assert 'league.tables.item.types' in sys.modules
    assert 'league.tables.reset' in sys.modules
    assert 'league.tables.response.libs' in sys.modules
    assert 'league.tables.response.types' in sys.modules
    assert 'league.tables.sessions' in sys.modules
    assert 'league.tables.users' in sys.modules


@pytest.mark.reset_table
def test_get_reset_item(
    reset_table_with_item: Table,
    reset_item: ResetItem,
    mocker: MockFixture,
) -> None:
    """Test that get_item call retrieves the expected ResetItem"""
    from layers.tables.python.league.tables.reset import get_reset_item

    reset_id = reset_item['reset_id']

    mock_get_item_response = mocker.patch(
        'layers.tables.python.league.tables.reset.get_item_response',
        side_effect=lambda x: x,
    )

    response = get_reset_item(reset_table_with_item, reset_id)

    assert mock_get_item_response.call_count == 1
    assert response['Item'] == reset_item


@pytest.mark.reset_table
def test_put_reset_item(
    reset_table: Table,
    reset_item: ResetItem,
    mocker: MockFixture,
) -> None:
    """Test that the put_item call puts a ResetItem into the table"""
    from layers.tables.python.league.tables.reset import put_reset_item

    mock_put_item_response = mocker.patch(
        'layers.tables.python.league.tables.reset.put_item_response',
        side_effect=lambda x: x,
    )

    reset_id = reset_item['reset_id']
    put_reset_item(reset_table, reset_item)

    get_response = reset_table.get_item(Key={'reset_id': reset_id})

    assert mock_put_item_response.call_count == 1
    assert get_response['Item'] == reset_item


@pytest.mark.reset_table
def test_reset_method_exceptions(
    reset_table_client_error: Table,
    reset_client_error: ClientError,
    reset_item: ResetItem,
    mocker: MockFixture,
) -> None:
    """Test that exceptions are handled for get_item and put_item calls.
    Reflect the ClientError back to make sure the correct exception is being
    tested against"""
    from layers.tables.python.league.tables.reset import (
        get_reset_item,
        put_reset_item,
    )

    mock_table_exception_response = mocker.patch(
        'layers.tables.python.league.tables.reset.item_exception_response',
        side_effect=lambda x: x,
    )

    reset_id = 'DoesNotMatter'

    exception_response = get_reset_item(reset_table_client_error, reset_id)
    error = exception_response.response['Error']

    assert mock_table_exception_response.call_count == 1
    assert re.search('GetItem', str(exception_response))
    assert error['Code'] == reset_client_error['Error']['Code']
    assert error['Message'] == reset_client_error['Error']['Message']

    exception_response = put_reset_item(reset_table_client_error, reset_item)
    error = exception_response.response['Error']

    assert mock_table_exception_response.call_count == 2
    assert re.search('PutItem', str(exception_response))
    assert error['Code'] == reset_client_error['Error']['Code']
    assert error['Message'] == reset_client_error['Error']['Message']
