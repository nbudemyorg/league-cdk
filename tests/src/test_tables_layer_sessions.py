import re
import sys
from typing import Any

import pytest
from pytest_mock import MockFixture
from types_boto3_dynamodb.service_resource import Table

from layers.tables.python.league.tables.item.types import SessionItem


@pytest.mark.sessions_table
def test_mocked_modules(mock_league_tables_layer: None) -> None:
    """Import mocked modules for subsequent tests"""
    assert 'league.tables.item.libs' in sys.modules
    assert 'league.tables.item.types' in sys.modules
    assert 'league.tables.reset' in sys.modules
    assert 'league.tables.response.libs' in sys.modules
    assert 'league.tables.response.types' in sys.modules
    assert 'league.tables.sessions' in sys.modules
    assert 'league.tables.users' in sys.modules


@pytest.mark.sessions_table
def test_get_sessions_item(
    sessions_table_with_session: Table,
    session_item: SessionItem,
    mocker: MockFixture,
) -> None:
    """Test that get_item call retrieves the expected SessionItem"""
    from layers.tables.python.league.tables.sessions import get_sessions_item

    mock_get_item_response = mocker.patch(
        'layers.tables.python.league.tables.sessions.get_item_response',
        side_effect=lambda x: x,
    )

    player_id = session_item['player_id']
    session_id = session_item['session_id']

    response = get_sessions_item(
        sessions_table_with_session, player_id, session_id
    )

    assert mock_get_item_response.call_count == 1
    assert response['Item'] == session_item


@pytest.mark.sessions_table
def test_put_sessions_item(
    sessions_table: Table,
    session_item: SessionItem,
    mocker: MockFixture,
) -> None:
    """Test that the put_item call puts a new SessionItem into the table"""
    from layers.tables.python.league.tables.sessions import put_sessions_item

    mock_put_item_response = mocker.patch(
        'layers.tables.python.league.tables.sessions.put_item_response',
        side_effect=lambda x: x,
    )

    put_sessions_item(sessions_table, session_item)

    get_response = sessions_table.get_item(Key=session_item)

    assert mock_put_item_response.call_count == 1
    assert get_response['Item'] == session_item


@pytest.mark.sessions_table
def test_sessions_method_exceptions(
    sessions_table_client_error: Table,
    sessions_client_error: dict[str, Any],
    session_item: SessionItem,
    mocker: MockFixture,
) -> None:
    """Test that ClientError exceptions are handled for get_item and put_item
    calls. Reflect the ClientError back to make sure the correct exception is
    being tested against"""
    from layers.tables.python.league.tables.sessions import (
        get_sessions_item,
        put_sessions_item,
    )

    mock_item_exception_response = mocker.patch(
        'layers.tables.python.league.tables.sessions.item_exception_response',
        side_effect=lambda x: x,
    )

    player_id = 'DoesNotMatter'
    session_id = 'DoesNotMatter'

    exception_response = get_sessions_item(
        sessions_table_client_error, player_id, session_id
    )
    error = exception_response.response['Error']

    assert mock_item_exception_response.call_count == 1
    assert re.search('GetItem', str(exception_response))
    assert error['Code'] == sessions_client_error['Error']['Code']
    assert error['Message'] == sessions_client_error['Error']['Message']

    exception_response = put_sessions_item(
        sessions_table_client_error, session_item
    )
    error = exception_response.response['Error']

    assert mock_item_exception_response.call_count == 2
    assert re.search('PutItem', str(exception_response))
    assert error['Code'] == sessions_client_error['Error']['Code']
    assert error['Message'] == sessions_client_error['Error']['Message']
