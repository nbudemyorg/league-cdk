import pytest
from pytest_mock import MockerFixture


@pytest.mark.sessions
def test_generate_password_hash(mocker: MockerFixture) -> None:
    """Test generate_password_hash returns a mocked hashed password"""

    from layers.sessions.python.league.credentials import (
        generate_password_hash,
    )

    mock_bcrypt = mocker.patch(
        'layers.sessions.python.league.credentials.bcrypt'
    )
    mock_bcrypt.hashpw.return_value = b'MockGeneratedHash'
    mock_bcrypt.gensalt.return_value = 'PinchOfSalt'

    response = generate_password_hash('AnyOldPassword')

    assert type(response) is str
    assert response == 'MockGeneratedHash'
