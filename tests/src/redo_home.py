import sys

import pytest
from pytest_mock import MockerFixture
from types_boto3_dynamodb.service_resource import Table


@pytest.fixture
def event_cookies():
    yield {
        'headers': {
            'cookie': {
                'player_id': 'DoesNotMatter',
                'session_id': 'DoesNotMatter',
            }
        }
    }


@pytest.mark.homepage
def test_mocked_modules_imported(
    mock_html_layer: None, mock_league_tables_layer: None
) -> None:
    """Test mocked modules were imported"""

    assert 'league' in sys.modules
    assert 'html_layer' in sys.modules


@pytest.mark.homepage
def test_lambda_handler_no_cookies_401(
    event_cookies: dict[str, str], sessions_table: Table
) -> None:
    """Test for 401 response when no session cookies supplied"""

    from src.home_page.get.home_get import lambda_handler

    del event_cookies['headers']['cookie']

    response = lambda_handler(event_cookies, {})

    assert response['statusCode'] == 401
    assert response['headers']['Content-Type'] == 'text/html'


@pytest.mark.homepage
def test_lambda_handler_no_session_cookie_401(
    event_cookies: dict[str, str], sessions_table: Table
) -> None:
    """Test for 401 response when no session_id cookie supplied"""

    from src.home_page.get.home_get import lambda_handler

    del event_cookies['headers']['cookie']['session_id']

    response = lambda_handler(event_cookies, {})

    assert response['statusCode'] == 401
    assert response['headers']['Content-Type'] == 'text/html'


@pytest.mark.homepage
def test_lambda_handler_no_player_cookie_401(
    event_cookies: dict[str, str], sessions_table: Table
) -> None:
    """Test for 401 response when no player_id cookie supplied"""

    from src.home_page.get.home_get import lambda_handler

    del event_cookies['headers']['cookie']['player_id']

    response = lambda_handler(event_cookies, {})

    assert response['statusCode'] == 401
    assert response['headers']['Content-Type'] == 'text/html'


@pytest.mark.homepage
def test_lambda_handler_valid_session_200_403_500(
    mocker: MockerFixture, event_cookies: dict[str, str], sessions_table: Table
) -> None:
    """Test response object based on valid_session mocked side_effects"""

    mock_valid_session = mocker.patch(
        'src.home_page.get.home_get.valid_session'
    )
    mock_valid_session.side_effect = [True, False, None]
    from src.home_page.get.home_get import lambda_handler

    response = lambda_handler(event_cookies, {})

    assert response['statusCode'] == 200
    assert response['headers']['Content-Type'] == 'text/html'
    assert mock_valid_session.call_count == 1

    response = lambda_handler(event_cookies, {})

    assert response['statusCode'] == 403
    assert response['headers']['Content-Type'] == 'text/html'
    assert mock_valid_session.call_count == 2

    response = lambda_handler(event_cookies, {})

    assert response['statusCode'] == 500
    assert response['headers']['Content-Type'] == 'text/html'
    assert mock_valid_session.call_count == 3
