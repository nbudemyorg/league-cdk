import sys

import pytest
from types_boto3_dynamodb.service_resource import Table
from types_boto3_secretsmanager.client import SecretsManagerClient

PASSWORD_VARIATIONS = [
    ('tooshort', 'PlayerOne', False),
    ('missing_upper_number', 'PlayerOne', False),
    ('Missing_number', 'PlayerOne', False),
    ('missing_upper1', 'PlayerOne', False),
    ('PlayerOne123', 'PlayerOne', False),
    ('playerone1a', 'PlayerOne', False),
    ('PLAYERONE1a', 'PlayerOne', False),
]

FORM_MISSING_PARAM = [
    ('player_id=New_User', None),
    ('player_id=New_User&password=bobbins', None),
    ('player_id=New_User&password=bobbins&email=bob@hotmail.com', None),
    ('password=bobbins', None),
    ('password=bobbins&invite=CorrectValue', None),
    ('password=bobbins&invite=CorrectValue&email=bob@hotmail.com', None),
    ('invite=CorrectValue', None),
    ('invite=CorrectValue,player_id=New_User&', None),
    ('invite=CorrectValue,player_id=New_User&email=bob@hotmail.com', None),
    ('email=bob@hotmail.com', None),
    ('email=bob@hotmail.com&invite=CorrectValue', None),
    ('email=bob@hotmail.com&invite=CorrectValue&password=bobbins', None),
]


DELIVERY_CHECK = False


@pytest.mark.registration
def test_mocked_modules_imported(
    mock_bcrypt_module: None,
    mock_auth_layer: None,
) -> None:
    """Test successful mocked import of modules"""

    assert 'auth_layer' in sys.modules
    assert 'bcrypt' in sys.modules


@pytest.mark.registration
def test_create_user_item_success(
    users_table: Table,
    monkeypatch: pytest.MonkeyPatch,
    test_user: dict[str, str],
    invitation_secret: SecretsManagerClient,
) -> None:
    """Test successful creation of a new Item in the Users DynamoDB table"""

    from src.user_registration.post.register_post import create_user_item

    new_player = test_user['player_id']
    stub_hash = test_user['password']
    email = test_user['email']

    response = create_user_item(users_table, new_player, stub_hash, email)

    user_item = users_table.get_item(Key={'player_id': new_player})

    assert response
    assert user_item['Item']['player_id'] == new_player
    assert user_item['Item']['password'] == stub_hash
    assert user_item['Item']['email'] == email


@pytest.mark.registration
def test_create_user_item_exception(
    users_table_client_error: Table, invitation_secret: SecretsManagerClient
) -> None:
    """Test create_user_item handles AWS ClientError exception"""

    from src.user_registration.post.register_post import create_user_item

    response = create_user_item(
        users_table_client_error, 'DoesNotMatter', 'DoesNotMatter', 'bogus'
    )

    assert not response


@pytest.mark.registration
def test_valid_invitation_key_true(
    invitation_secret: SecretsManagerClient,
) -> None:
    """Test valid_invitation_key returns True when valid key provided"""

    from src.user_registration.post.register_post import valid_invitation_key

    response = valid_invitation_key('CorrectValue')

    assert response


@pytest.mark.registration
def test_valid_invitation_key_false(
    invitation_secret: SecretsManagerClient,
) -> None:
    """Test valid_invitation_key returns False when invalid key provided"""

    from src.user_registration.post.register_post import valid_invitation_key

    response = valid_invitation_key('IncorrectValue')

    assert not response


@pytest.mark.parametrize(
    'password, player, expected_result', PASSWORD_VARIATIONS
)
@pytest.mark.registration
def test_password_meets_criteria(
    password: str,
    player: str,
    expected_result: bool,
    invitation_secret: SecretsManagerClient,
) -> None:
    """Tests to make sure supplied password conforms to defined standard"""

    from src.user_registration.post.register_post import (
        password_meets_criteria,
    )

    assert password_meets_criteria(password, player) is expected_result


@pytest.mark.parametrize('form_data, expected_result', FORM_MISSING_PARAM)
@pytest.mark.registration
def test_invalid_form_data(
    form_data: str,
    expected_result: bool,
    invitation_secret: SecretsManagerClient,
) -> None:
    """Test that missing form data results in False being returned"""

    from src.user_registration.post.register_post import form_data_valid

    assert form_data_valid(form_data, DELIVERY_CHECK) is expected_result


@pytest.mark.registration
def test_valid_form_data(invitation_secret: SecretsManagerClient) -> None:
    """Test expected dict is returned when all form params supplied"""

    valid_form_params = (
        'player_id=PyTest_Player&password=NotVerySecure&'
        'invite=PyTestInvite&email=bob@hotmail.com'
    )

    expected_result = {
        'player_id': 'PyTest_Player',
        'password': 'NotVerySecure',
        'invite': 'PyTestInvite',
        'email': 'bob@hotmail.com',
    }

    from src.user_registration.post.register_post import form_data_valid

    response = form_data_valid(valid_form_params, DELIVERY_CHECK)

    assert response == expected_result


@pytest.mark.registration
def test_player_id_exists_true(
    monkeypatch: pytest.MonkeyPatch,
    users_table: Table,
) -> None:
    """player_id_exists returns True if the call to get_player_item
    returns an item with matching player_id"""

    from src.user_registration.post.register_post import player_id_exists

    patched_response = {'player_id': 'AnyOldUser'}
    monkeypatch.setattr(
        'src.user_registration.post.register_post.get_player_item',
        lambda table, supplied_id: patched_response,
    )

    response = player_id_exists(users_table, 'AnyOldUser')

    assert response is True


@pytest.mark.registration
def test_player_id_exists_false(
    monkeypatch: pytest.MonkeyPatch,
    users_table: Table,
) -> None:
    """player_id_exists returns False if the call to get_player_item
    does not return an item for that player_id"""

    from src.user_registration.post.register_post import player_id_exists

    patched_response = {'id_not_found': 'AnyOldUser'}
    monkeypatch.setattr(
        'src.user_registration.post.register_post.get_player_item',
        lambda table, supplied_id: patched_response,
    )

    response = player_id_exists(users_table, 'AnyOldUser')

    assert response is False


@pytest.mark.registration
def test_player_id_exists_exception(
    monkeypatch: pytest.MonkeyPatch,
    users_table: Table,
) -> None:
    """player_id_exists returns None if the call to get_player_item
    results in a ClientError exception"""

    from src.user_registration.post.register_post import player_id_exists

    patched_response = None
    monkeypatch.setattr(
        'src.user_registration.post.register_post.get_player_item',
        lambda table, supplied_id: patched_response,
    )

    response = player_id_exists(users_table, 'AnyOldUser')

    assert response is None
