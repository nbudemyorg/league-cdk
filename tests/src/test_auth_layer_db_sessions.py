from datetime import datetime, timedelta

import pytest
from freezegun import freeze_time
from types_boto3_dynamodb.service_resource import Table

from layers.sessions.python.auth_layer import (
    COOKIE_MAX_AGE,
    create_login_response,
    create_session_item,
    valid_session,
)


@pytest.mark.sessions
def test_create_session_item(
    sessions_table: Table, session_item: dict[str, str], frozen_date: datetime
) -> None:
    """Test session item is created for given player_id"""

    with freeze_time(frozen_date):
        create_session_item(sessions_table, session_item['player_id'])
        moto_get_item = sessions_table.get_item(Key=session_item)

        expected_expiry = frozen_date + timedelta(seconds=COOKIE_MAX_AGE)
        expected_item = session_item
        expected_item['expiry'] = expected_expiry.isoformat()

        assert moto_get_item['Item'] == expected_item


@pytest.mark.sessions
def test_valid_session_with_item(
    sessions_table: Table, session_item: dict[str, str], frozen_date: datetime
) -> None:
    """Test function handles unexpired valid session item for a given user"""

    valid_session_expiry = frozen_date + timedelta(hours=1)
    session_item['expiry'] = valid_session_expiry.isoformat()

    with freeze_time(frozen_date):
        sessions_table.put_item(Item=session_item)

        session_is_valid = valid_session(
            sessions_table,
            session_item['player_id'],
            session_item['session_id'],
        )

    assert session_is_valid


@pytest.mark.sessions
def test_valid_session_expired_item(
    sessions_table: Table, session_item: dict[str, str], frozen_date: datetime
) -> None:
    """Test function handles an expired session item for a given user"""

    valid_session_expiry = frozen_date - timedelta(hours=1)
    session_item['expiry'] = valid_session_expiry.isoformat()

    with freeze_time(frozen_date):
        sessions_table.put_item(Item=session_item)

        session_is_valid = valid_session(
            sessions_table,
            session_item['player_id'],
            session_item['session_id'],
        )

    assert not session_is_valid


@pytest.mark.sessions
def test_valid_session_without_item(sessions_table: Table) -> None:
    """Test function returns False if no session item is found for a user"""

    session_is_valid = valid_session(
        sessions_table, player='bob', session='NoSessionWasCreated'
    )

    assert not session_is_valid


@pytest.mark.sessions
def test_create_login_response() -> None:

    player_id = 'PlayerOne'
    session_id = 'DoesNotMatter'

    login_response = create_login_response(
        player=player_id, session=session_id
    )

    assert login_response['statusCode'] == 301
    assert isinstance(login_response['multiValueHeaders']['Location'], list)
    assert isinstance(login_response['multiValueHeaders']['Set-Cookie'], list)

    set_cookies = login_response['multiValueHeaders']['Set-Cookie']

    assert f'session_id={session_id}; Max-Age={COOKIE_MAX_AGE}' in set_cookies
    assert f'player_id={player_id}; Max-Age={COOKIE_MAX_AGE}' in set_cookies
