import re
import sys
from typing import Any

import pytest
from pytest_mock import MockFixture
from types_boto3_dynamodb.service_resource import Table

from layers.tables.python.league.tables.item.types import UserItem


@pytest.mark.users_table
def test_mocked_modules(mock_league_tables_layer: None) -> None:
    """Import mocked modules for subsequent tests"""
    assert 'league.tables.item.libs' in sys.modules
    assert 'league.tables.item.types' in sys.modules
    assert 'league.tables.password_reset' in sys.modules
    assert 'league.tables.response.libs' in sys.modules
    assert 'league.tables.response.types' in sys.modules
    assert 'league.tables.sessions' in sys.modules
    assert 'league.tables.users' in sys.modules


@pytest.mark.users_table
def test_get_users_item(
    users_table_with_user: Table, test_user: UserItem, mocker: MockFixture
) -> None:
    """Test get_item response gets expected users table item"""
    from layers.tables.python.league.tables.users import get_users_item

    mock_get_item_response = mocker.patch(
        'layers.tables.python.league.tables.users.get_item_response',
        side_effect=lambda x: x,
    )

    player_id = test_user['player_id']
    response = get_users_item(users_table_with_user, player_id)

    assert mock_get_item_response.call_count == 1
    assert response['Item'] == test_user


@pytest.mark.users_table
def test_users_method_exceptions(
    users_table_client_error: Table,
    mocker: MockFixture,
    users_client_error: dict[str, Any],
) -> None:
    """Test all exceptions are handled for the users table methods. Reflect
    the ClientError back to make sure the correct exception is being tested
    against"""
    from layers.tables.python.league.tables.users import (
        get_users_item,
        put_users_item,
        update_users_item,
    )

    mock_table_method_response = mocker.patch(
        'layers.tables.python.league.tables.users.item_exception_response',
        side_effect=lambda x: x,
    )

    exception_response = get_users_item(users_table_client_error, 'Any_user')
    error = exception_response.response['Error']

    assert mock_table_method_response.call_count == 1
    assert re.search('GetItem', str(exception_response))
    assert error['Code'] == users_client_error['Error']['Code']
    assert error['Message'] == users_client_error['Error']['Message']

    exception_response = put_users_item(users_table_client_error, 'Any_user')
    error = exception_response.response['Error']

    assert mock_table_method_response.call_count == 2
    assert re.search('PutItem', str(exception_response))
    assert error['Code'] == users_client_error['Error']['Code']
    assert error['Message'] == users_client_error['Error']['Message']

    exception_response = update_users_item(
        users_table_client_error,
        'Any_user',
        'token',
    )
    error = exception_response.response['Error']

    assert mock_table_method_response.call_count == 3
    assert re.search('UpdateItem', str(exception_response))
    assert error['Code'] == users_client_error['Error']['Code']
    assert error['Message'] == users_client_error['Error']['Message']


@pytest.mark.users_table
def test_put_users_item(
    users_table: Table, test_user: UserItem, mocker: MockFixture
) -> None:
    """Test the put_item call for the users table creates a new user item"""
    from layers.tables.python.league.tables.users import put_users_item

    mock_put_item_response = mocker.patch(
        'layers.tables.python.league.tables.users.put_item_response',
        side_effect=lambda x: x,
    )

    player_id = test_user['player_id']

    put_users_item(users_table, test_user)

    get_response = users_table.get_item(Key={'player_id': player_id})

    assert get_response['Item'] == test_user


@pytest.mark.users_table
def test_update_users_item(
    users_table_with_user: Table, mocker: MockFixture, test_user: UserItem
) -> None:
    """Test the update_item call updates an existing item as expected
    within the users table"""
    from layers.tables.python.league.tables.users import update_users_item

    mock_put_item_response = mocker.patch(
        'layers.tables.python.league.tables.users.update_item_response',
        side_effect=lambda x: x,
    )

    player_id = test_user['player_id']
    token = 'NotReallyATokenButWillDo'
    test_user['reset_id'] = token

    update_users_item(users_table_with_user, player_id, token)

    get_response = users_table_with_user.get_item(Key={'player_id': player_id})

    assert get_response['Item'] == test_user
