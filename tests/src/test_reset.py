import sys
from datetime import UTC, datetime, timedelta
from decimal import Decimal

import pytest
from freezegun import freeze_time
from types_boto3_dynamodb.service_resource import Table


@pytest.mark.reset
def test_mocked_modules(mock_auth_layer: None) -> None:
    assert 'auth_layer' in sys.modules


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


@pytest.mark.reset
def test_create_reset_item(
    password_reset_table: Table,
    test_user: dict[str, str],
    frozen_date: datetime,
) -> None:
    from src.password_reset.post.reset_post import (
        SECONDS_VALID,
        create_reset_item,
    )

    url_safe_string = 'ThisWillHaveToDo'
    player_id = test_user['player_id']
    test_user['reset_id'] = url_safe_string

    with freeze_time(frozen_date):
        expected_expiry = datetime.now(UTC) + timedelta(seconds=SECONDS_VALID)
        expected_expiry_str = expected_expiry.isoformat()
        expected_ttl = Decimal(expected_expiry.timestamp())
        expected_item = {
            'reset_id': url_safe_string,
            'player_id': player_id,
            'expiry': expected_expiry_str,
            'ttl': expected_ttl,
        }

        assert create_reset_item(password_reset_table, test_user) is True

        response = password_reset_table.get_item(
            Key={'reset_id': url_safe_string}
        )

        assert response['Item'] == expected_item


@pytest.mark.reset
def test_create_reset_exception(
    password_reset_table_client_error: Table,
    test_user: dict[str, str],
    frozen_date: datetime,
) -> None:
    from src.password_reset.post.reset_post import create_reset_item

    url_safe_string = 'DoesNotMatterAtAll'
    test_user['reset_id'] = url_safe_string

    with freeze_time(frozen_date):
        assert (
            create_reset_item(password_reset_table_client_error, test_user)
            is None
        )
