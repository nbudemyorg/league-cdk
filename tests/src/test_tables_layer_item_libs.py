import sys
from datetime import datetime, timedelta

import pytest
from freezegun import freeze_time
from pytest_mock import MockerFixture

from layers.tables.python.league.tables.item.types import UserItem

MOCK_UUID4 = '12345678-1234-4678-8234-567812345678'


@pytest.mark.item_libs
def test_mocked_modules(
    mock_league_tables_layer: None, mock_html_layer: None
) -> None:
    assert 'league.tables.item.libs' in sys.modules
    assert 'league.tables.item.types' in sys.modules
    assert 'league.tables.reset' in sys.modules
    assert 'league.tables.response.libs' in sys.modules
    assert 'league.tables.response.types' in sys.modules
    assert 'league.tables.sessions' in sys.modules
    assert 'league.tables.users' in sys.modules
    assert 'league.static.pages' in sys.modules


@pytest.mark.item_libs
def test_create_session_item(
    frozen_date: datetime, mocker: MockerFixture
) -> None:
    """Test that a valid Sessions table item is created"""
    from layers.tables.python.league.tables.item.libs import (
        ADD_TTL,
        COOKIE_MAX_AGE,
        create_session_item,
    )

    player_id = 'PlayerOne'
    session_expiry = frozen_date + timedelta(seconds=COOKIE_MAX_AGE)

    mock_uuid = mocker.patch(
        'layers.tables.python.league.tables.item.libs.uuid4',
        return_value=MOCK_UUID4,
    )

    with freeze_time(frozen_date):
        session_item = create_session_item(player_id)

        assert session_item['player_id'] == player_id
        assert session_item['session_id'] == MOCK_UUID4
        assert session_item['expiry'] == session_expiry.isoformat()
        assert session_item['ttl'] == int(session_expiry.timestamp() + ADD_TTL)

    assert mock_uuid.call_count == 1


@pytest.mark.item_libs
def test_create_user_item(test_user: UserItem) -> None:
    """Test that a valid Users table item is created"""
    from layers.tables.python.league.tables.item.libs import create_user_item

    player_id = test_user['player_id']
    hashed_password = test_user['password']
    email = test_user['email']

    user_item = create_user_item(player_id, hashed_password, email)

    assert user_item == test_user


@pytest.mark.item_libs
def test_create_reset_item(
    frozen_date: datetime, mocker: MockerFixture
) -> None:
    """Test that a valid PasswordReset table item is created"""
    from layers.tables.python.league.tables.item.libs import (
        SECONDS_VALID,
        create_reset_item,
    )

    player_id = 'PlayerOne'
    urlsafe_response = 'ThisWillHaveToDo'
    expected_expiry = frozen_date + timedelta(seconds=SECONDS_VALID)

    mock_urlsafe = mocker.patch(
        'layers.tables.python.league.tables.item.libs.token_urlsafe',
        return_value=urlsafe_response,
    )

    with freeze_time(frozen_date):
        reset_item = create_reset_item(player_id)

        assert reset_item['reset_id'] == urlsafe_response
        assert reset_item['player_id'] == player_id
        assert reset_item['expiry'] == expected_expiry.isoformat()
        assert reset_item['ttl'] == int(expected_expiry.timestamp())

    assert mock_urlsafe.call_count == 1
