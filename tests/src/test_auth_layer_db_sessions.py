from datetime import datetime, timedelta

import pytest
from freezegun import freeze_time
from pytest_mock import MockerFixture
from types_boto3_dynamodb.service_resource import Table

from layers.sessions.python.auth_layer import (
    COOKIE_MAX_AGE,
    create_login_response,
    valid_session,
)


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


@pytest.mark.sessions
def test_put_player_item_token_true(
    users_table: Table,
    test_user: dict[str, str],
    monkeypatch: pytest.MonkeyPatch,
) -> None:

    from layers.sessions.python.auth_layer import put_player_item

    url_safe_token = 'ThisWillHaveToDo'
    expected_item = test_user
    expected_item['reset_id'] = url_safe_token
    player_id = test_user['player_id']

    monkeypatch.setattr(
        'layers.sessions.python.auth_layer.secrets.token_urlsafe',
        lambda: url_safe_token,
    )

    put_response = put_player_item(users_table, test_user, reset_token=True)

    get_response = users_table.get_item(Key={'player_id': player_id})

    assert put_response == get_response['Item']


@pytest.mark.sessions
def test_put_player_item_token_false(
    users_table: Table,
    test_user: dict[str, str],
) -> None:

    from layers.sessions.python.auth_layer import put_player_item

    player_id = test_user['player_id']

    put_response = put_player_item(users_table, test_user)

    get_response = users_table.get_item(Key={'player_id': player_id})

    assert put_response == get_response['Item']


@pytest.mark.sessions
def test_put_player_item_exception(
    users_table_client_error: Table,
    test_user: dict[str, str],
) -> None:

    from layers.sessions.python.auth_layer import put_player_item

    put_response = put_player_item(users_table_client_error, test_user)

    assert put_response is None
