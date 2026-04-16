import sys

import pytest
from pytest_mock import MockerFixture
from types_boto3_dynamodb.service_resource import Table

LOGIN_FORM_VARIATIONS = [
    ('player_id=New_User', None),
    ('password=bobbins', None),
    ('neverused=anything', None),
]


@pytest.mark.login
def test_mocked_modules_imported(
    mock_auth_layer: None, mock_bcrypt_module: None
) -> None:
    """Test mocked modules are imported"""

    assert 'auth_layer' in sys.modules
    assert 'bcrypt' in sys.modules


@pytest.mark.parametrize('form_string, expected_result', LOGIN_FORM_VARIATIONS)
@pytest.mark.login
def test_invalid_form_data(form_string: str, expected_result: bool) -> None:
    """Test missing login form parameters are handled"""

    from src.user_login.post.login_post import valid_form_data

    assert valid_form_data(form_string) is expected_result


@pytest.mark.login
def test_valid_form_data() -> None:
    """Test valid login form params return expected dict"""

    from src.user_login.post.login_post import valid_form_data

    valid_form_params = 'player_id=The_Username&password=NotAHasButGoodEnough'
    expected_result = {
        'player_id': 'The_Username',
        'password': 'NotAHasButGoodEnough',
    }

    assert valid_form_data(valid_form_params) == expected_result


@pytest.mark.login
def test_password_is_valid_checkpw(
    users_table_with_user: Table,
    mocker: MockerFixture,
    test_user: dict[str, str],
) -> None:
    """Test that bcrypt.checkpw return value is returned by function"""

    from src.user_login.post.login_post import password_is_valid

    mock_bcrypt = mocker.patch('src.user_login.post.login_post.bcrypt.checkpw')
    mock_bcrypt.side_effect = [True, False]

    player = test_user['player_id']
    password = 'DoesNotMatter'
    response = password_is_valid(users_table_with_user, player, password)

    assert mock_bcrypt.call_count == 1
    assert response

    response = password_is_valid(users_table_with_user, player, password)

    assert not response
    assert mock_bcrypt.call_count == 2


@pytest.mark.login
def test_password_is_valid_no_user_found(
    users_table: Table, test_user: dict[str, str]
) -> None:
    """Test False is returned when player item does not exist in db"""

    from src.user_login.post.login_post import password_is_valid

    player = 'DoesNotExist'
    password = 'DoesNotMatter'
    response = password_is_valid(users_table, player, password)

    assert not response


@pytest.mark.login
def test_password_is_valid_client_error(
    users_table_client_error: Table,
) -> None:
    """Test function handles AWS ClientError exception for db read"""

    from src.user_login.post.login_post import password_is_valid

    player = 'DoesNotMatter'
    password = 'DoesNotMatter'
    response = password_is_valid(users_table_client_error, player, password)

    assert response is None
