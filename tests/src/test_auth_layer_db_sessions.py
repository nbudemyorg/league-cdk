import pytest
from types_boto3_dynamodb.service_resource import Table

from layers.sessions.python.auth_layer import (
    COOKIE_MAX_AGE,
    create_login_response,
    create_session_item,
    valid_session,
)


@pytest.mark.sessions
def test_create_session_item(
    sessions_table: Table, session_item: dict[str, str]
) -> None:
    """Test session item is created for given player_id"""

    create_session_item(sessions_table, session_item['player_id'])

    mocked_get_item = sessions_table.get_item(Key=session_item)

    assert mocked_get_item['Item'] == session_item


@pytest.mark.sessions
def test_valid_session_with_item(
    sessions_table: Table, session_item: dict[str, str]
) -> None:
    """Test function retrieves created valid session item for a given user"""

    sessions_table.put_item(Item=session_item)

    session_is_valid = valid_session(
        sessions_table, session_item['player_id'], session_item['session_id']
    )

    assert session_is_valid


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
    expires_seconds = 3600

    login_response = create_login_response(
        player=player_id, session=session_id
    )

    assert login_response['statusCode'] == 301
    assert isinstance(login_response['multiValueHeaders']['Location'], list)
    assert  isinstance(
        login_response['multiValueHeaders']['Set-Cookie'], list
    )

    set_cookies = login_response['multiValueHeaders']['Set-Cookie']

    assert f'session_id={session_id}; Max-Age={COOKIE_MAX_AGE}' in set_cookies
    assert f'player_id={player_id}; Max-Age={COOKIE_MAX_AGE}' in set_cookies
