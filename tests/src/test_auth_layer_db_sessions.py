from datetime import datetime, timedelta

import pytest
from freezegun import freeze_time
from pytest_mock import MockerFixture
from types_boto3_dynamodb.service_resource import Table

from layers.sessions.python.auth_layer import (
    ADD_TTL,
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
        expected_ttl = int(expected_expiry.timestamp() + ADD_TTL)
        expected_item = session_item
        expected_item['expiry'] = expected_expiry.isoformat()
        expected_item['ttl'] = expected_ttl

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


@pytest.mark.sessions
def test_generate_password_hash(mocker: MockerFixture) -> None:
    """Test generate_password_hash returns a mocked hashed password"""

    from layers.sessions.python.auth_layer import generate_password_hash

    mock_bcrypt = mocker.patch('layers.sessions.python.auth_layer.bcrypt')
    mock_bcrypt.hashpw.return_value = b'MockGeneratedHash'
    mock_bcrypt.gensalt.return_value = 'PinchOfSalt'

    response = generate_password_hash('AnyOldPassword')

    assert type(response) is str
    assert response == 'MockGeneratedHash'


@pytest.mark.sessions
def test_get_player_item_true(
    users_table_with_user: Table,
    test_user: dict[str, str],
) -> None:

    from layers.sessions.python.auth_layer import get_player_item

    new_player = test_user['player_id']

    response = get_player_item(users_table_with_user, new_player)

    assert response == test_user


@pytest.mark.sessions
def test_get_player_item_false(users_table: Table) -> None:

    from layers.sessions.python.auth_layer import get_player_item

    player_id = 'NoSuchUser'

    response = get_player_item(users_table, player_id)

    assert response == {'id_not_found': player_id}


@pytest.mark.sessions
def test_get_player_item_exception(users_table_client_error) -> None:
    from layers.sessions.python.auth_layer import get_player_item

    player_id = 'NoSuchUser'

    response = get_player_item(users_table_client_error, player_id)

    assert response is None
