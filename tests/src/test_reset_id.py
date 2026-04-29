import sys
from datetime import UTC, datetime, timedelta

import pytest
from freezegun import freeze_time


@pytest.mark.resetid
def test_mocked_modules(
    mock_league_tables_layer: None, mock_html_layer: None
) -> None:
    assert 'league' in sys.modules
    assert 'html_layer' in sys.modules


@pytest.mark.resetid
def test_reset_item_still_valid_true(frozen_date: datetime) -> None:
    from src.password_reset.id.get.reset_id_get import reset_item_still_valid

    with freeze_time(frozen_date):
        valid_token = datetime.now(UTC) + timedelta(seconds=60)
        test_item = {'expiry': valid_token.isoformat()}

        assert reset_item_still_valid(test_item) is True


@pytest.mark.resetid
def test_reset_item_still_valid_false(frozen_date: datetime) -> None:
    from src.password_reset.id.get.reset_id_get import reset_item_still_valid

    with freeze_time(frozen_date):
        valid_token = datetime.now(UTC) - timedelta(seconds=60)
        test_item = {'expiry': valid_token.isoformat()}

        assert reset_item_still_valid(test_item) is False
