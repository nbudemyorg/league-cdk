import sys

import pytest
from pytest_mock import MockerFixture
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
def test_player_id_exists_false(
    users_table: Table, invitation_secret: SecretsManagerClient
) -> None:
    """Test behavior when player id does not exist in db"""

    from src.user_registration.post.register_post import player_id_exists

    response = player_id_exists(users_table, 'Not_Created')

    assert not response


@pytest.mark.registration
def test_player_id_exists_true(
    users_table_with_user: Table,
    invitation_secret: SecretsManagerClient,
    test_user: dict[str, str],
) -> None:
    """Test behavior when player id does exist in db"""

    new_player = test_user['player_id']
    from src.user_registration.post.register_post import player_id_exists

    response = player_id_exists(users_table_with_user, new_player)

    assert response


@pytest.mark.registration
def test_player_id_exists_exception(
    users_table_client_error: Table, invitation_secret: SecretsManagerClient
) -> None:
    """Test player_id_exists handles AWS ClientError exception"""

    from src.user_registration.post.register_post import player_id_exists

    response = player_id_exists(users_table_client_error, 'DoesNotMatter')

    assert response is None


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


@pytest.mark.registration
def test_generate_password_hash(
    invitation_secret: SecretsManagerClient, mocker: MockerFixture
) -> None:
    """Test generate_password_hash returns a mocked hashed password"""

    from src.user_registration.post.register_post import generate_password_hash

    mock_bcrypt = mocker.patch(
        'src.user_registration.post.register_post.bcrypt'
    )
    mock_bcrypt.hashpw.return_value = b'MockGeneratedHash'
    mock_bcrypt.gensalt.return_value = 'PinchOfSalt'

    response = generate_password_hash('AnyOldPassword')

    assert type(response) is str
    assert response == 'MockGeneratedHash'


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
