import sys

import pytest
from types_boto3_secretsmanager.client import SecretsManagerClient

from layers.tables.python.league.tables.response_types import PutResult

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


@pytest.fixture
def users_put_result(test_user) -> PutResult:
    yield {'success': True, 'item': test_user, 'consumed_capacity': {}}


@pytest.fixture
def users_put_result_user_exists() -> PutResult:
    yield {
        'success': False,
        'error_code': 'ConditionalCheckFailedException',
        'consumed_capacity': {},
    }


@pytest.fixture
def users_put_result_client_err() -> PutResult:
    yield {
        'success': False,
        'error_code': 'AnyOtherErrorCode',
        'consumed_capacity': {},
    }


@pytest.mark.registration
def test_mocked_modules_imported(
    mock_bcrypt_module: None,
    mock_auth_layer: None,
    mock_league_tables_layer: None,
) -> None:
    """Test successful mocked import of modules"""

    assert 'auth_layer' in sys.modules
    assert 'bcrypt' in sys.modules
    assert 'league' in sys.modules


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
def test_user_already_exists_false(
    users_put_result: PutResult,
) -> None:
    """Returns False if the conditional put_item call response
    has key success:True"""

    from src.user_registration.post.register_post import user_already_exists

    response = user_already_exists(users_put_result)

    assert response is False


@pytest.mark.registration
def test_user_already_exists_true(
    users_put_result_user_exists: PutResult,
) -> None:
    """Returns True if the condtional put_item call raised an exception with
    error_code ConditionalCheckFailedException"""

    from src.user_registration.post.register_post import user_already_exists

    response = user_already_exists(users_put_result_user_exists)

    assert response is True


@pytest.mark.registration
def test_user_already_exists_exception(
    users_put_result_client_err: PutResult,
) -> None:
    """Returns None if the conditional put_item call raises any other
    ClientError error_code"""

    from src.user_registration.post.register_post import user_already_exists

    response = user_already_exists(users_put_result_client_err)

    assert response is None
