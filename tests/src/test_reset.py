import sys
from datetime import UTC, datetime, timedelta
from decimal import Decimal

import pytest
from freezegun import freeze_time
from types_boto3_dynamodb.service_resource import Table


@pytest.mark.reset
def test_mocked_modules(
    mock_auth_layer: None, mock_league_tables_layer
) -> None:

    assert 'auth_layer' in sys.modules
    assert 'league' in sys.modules


@pytest.mark.reset
def test_transform_validate(monkeypatch: pytest.MonkeyPatch):
    """Test that function rejects valid form submissions"""

    from src.password_reset.post.reset_post import transform_validate

    invalid_data_response = {'validated': 'false'}
    valid_data_response = {'player_id': 'bob', 'validated': 'true'}

    form_string = 'player_id='
    assert transform_validate(form_string) == invalid_data_response

    form_string = ''
    assert transform_validate(form_string) == invalid_data_response

    form_string = 'anything=else'
    assert transform_validate(form_string) == invalid_data_response

    form_string = 'just=rubbish&nothing=else'
    assert transform_validate(form_string) == invalid_data_response

    monkeypatch.setattr(
        'src.password_reset.post.reset_post.valid_player_id',
        lambda player_id: True,
    )

    form_string = 'player_id=bob'
    assert transform_validate(form_string) == valid_data_response


