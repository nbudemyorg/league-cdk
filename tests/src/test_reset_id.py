import sys
from typing import Any

import pytest


@pytest.fixture
def mock_api_event():
    yield {
        'pathParameters': {'resetId': 'MockResetId'},
        'body': 'new_password=DodgyPassword',
    }


@pytest.mark.resetid
def test_mocked_modules(mock_league_layer: None) -> None:
    assert 'league.content.libs' in sys.modules
    assert 'league.logger' in sys.modules
    assert 'league.tables.item.types' in sys.modules
    assert 'league.tables.reset' in sys.modules
    assert 'league.tables.response.types' in sys.modules


@pytest.mark.resetid
def test_process_event(mock_api_event: dict[str, Any]) -> None:
    from src.password_reset.id.post.reset_id_post import process_event

    response = process_event(mock_api_event)

    assert response['reset_id'] == 'MockResetId'
    assert response['new_password'] == 'DodgyPassword'

    del mock_api_event['body']
    response = process_event(mock_api_event)
    assert response['reset_id'] == 'MockResetId'
    assert response['new_password'] == 'missing'

    del mock_api_event['pathParameters']
    response = process_event(mock_api_event)
    assert response['reset_id'] == 'missing'
    assert response['new_password'] == 'missing'
