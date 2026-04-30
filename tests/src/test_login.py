import sys
from typing import Any

import pytest
from pytest_mock import MockerFixture
from types_boto3_dynamodb.service_resource import Table

LOGIN_FORM_VARIATIONS = [
    ('player_id=New_User', None),
    ('password=bobbins', None),
    ('neverused=anything', None),
]


@pytest.fixture
def mock_item_found_response():
    yield {
        'success': True,
        'item': {'player_id': 'A_user', 'password': 'DoesNotMatter'},
        'consumed_capacity': {},
    }


@pytest.fixture
def mock_get_item(
    mocker: MockerFixture, mock_item_found_response: dict[str, Any]
):
    yield mocker.patch(
        'src.user_login.post.login_post.get_users_item',
        return_value=mock_item_found_response,
    )


@pytest.fixture
def mock_get_no_item(
    mock_get_item: MockerFixture, mock_item_found_response: dict[str, Any]
):
    mock_item_found_response['item'] = {}
    mock_get_item.return_value = mock_item_found_response
    yield mock_get_item


@pytest.fixture
def mock_get_item_exception(
    mock_get_item: MockerFixture, mock_item_found_response: dict[str, Any]
):
    mock_item_found_response['success'] = False
    mock_get_item.return_value = mock_item_found_response
    yield mock_get_item


@pytest.mark.login
def test_mocked_modules_imported(
    mock_sessions_layer: None,
    mock_bcrypt_module: None,
    mock_league_tables_layer: None,
) -> None:
    """Test mocked modules are imported"""

    assert 'bcrypt' in sys.modules
    assert 'league.tables.item_libs' in sys.modules
    assert 'league.tables.item_types' in sys.modules
    assert 'league.tables.sessions' in sys.modules
    assert 'league.tables.users' in sys.modules
    assert 'league.auth' in sys.modules
    assert 'league.credentials' in sys.modules
    assert 'league.validate' in sys.modules


@pytest.mark.parametrize('form_string, expected_result', LOGIN_FORM_VARIATIONS)
@pytest.mark.login
def test_invalid_form_data(
    form_string: str,
    expected_result: bool,
    users_table: Table,
    sessions_table: Table,
) -> None:
    """Test missing login form parameters are handled"""

    from src.user_login.post.login_post import valid_form_data

    assert valid_form_data(form_string) is expected_result


@pytest.mark.login
def test_valid_form_data(
    users_table: Table,
    sessions_table: Table,
) -> None:
    """Test valid login form params return expected dict"""

    from src.user_login.post.login_post import valid_form_data

    valid_form_params = 'player_id=The_Username&password=NotAHashButGoodEnough'
    expected_result = {
        'player_id': 'The_Username',
        'password': 'NotAHashButGoodEnough',
    }

    assert valid_form_data(valid_form_params) == expected_result


@pytest.mark.login
def test_password_is_valid_checkpw(
    users_table: Table,
    sessions_table: Table,
    mocker: MockerFixture,
    mock_get_item: MockerFixture,
    test_user: dict[str, str],
) -> None:
    """Test that result of bcrypt.checkpw is returned by the function when a
    user password is verified as being valid and invalid"""

    from src.user_login.post.login_post import password_is_valid

    mock_bcrypt = mocker.patch('src.user_login.post.login_post.bcrypt.checkpw')
    mock_bcrypt.side_effect = [True, False]

    player = 'A_player'
    password = 'DoesNotMatter'
    response = password_is_valid(users_table, player, password)

    assert response
    assert mock_bcrypt.call_count == 1
    assert mock_get_item.call_count == 1

    response = password_is_valid(users_table, player, password)

    assert not response
    assert mock_bcrypt.call_count == 2
    assert mock_get_item.call_count == 2


@pytest.mark.login
def test_password_is_valid_no_user_found(
    users_table: Table,
    sessions_table: Table,
    mock_get_no_item: MockerFixture,
) -> None:
    """Test False is returned when item for player does not exist in db"""

    from src.user_login.post.login_post import password_is_valid

    player = 'DoesNotExist'
    password = 'DoesNotMatter'
    response = password_is_valid(users_table, player, password)

    assert response is False
    assert mock_get_no_item.call_count == 1


@pytest.mark.login
def test_password_is_valid_client_error(
    users_table: Table,
    sessions_table: Table,
    mock_get_item_exception: MockerFixture,
) -> None:
    """Test function handles AWS ClientError exception for db read"""

    from src.user_login.post.login_post import password_is_valid

    player = 'DoesNotMatter'
    password = 'DoesNotMatter'
    response = password_is_valid(users_table, player, password)

    assert response is None
    assert mock_get_item_exception.call_count == 1
