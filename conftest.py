import os
import sys
from datetime import UTC, datetime
from unittest.mock import MagicMock

import pytest

from tests.fixtures.tables.resets import (
    reset_client_error,
    reset_item,
    reset_table,
    reset_table_client_error,
    reset_table_with_item,
)
from tests.fixtures.tables.sessions import (
    session_item,
    sessions_client_error,
    sessions_table,
    sessions_table_client_error,
    sessions_table_with_session,
)
from tests.fixtures.tables.users import (
    test_user,
    users_client_error,
    users_table,
    users_table_client_error,
    users_table_with_user,
)


@pytest.fixture(scope='module')
def mock_bcrypt_module():
    sys.modules['bcrypt'] = MagicMock()


@pytest.fixture(scope='module')
def mock_league_layer():
    sys.modules['league.auth'] = MagicMock()
    sys.modules['league.aws_secrets'] = MagicMock()
    sys.modules['league.credentials'] = MagicMock()
    sys.modules['league.content.libs'] = MagicMock()
    sys.modules['league.logger'] = MagicMock()
    sys.modules['league.tables.item.types'] = MagicMock()
    sys.modules['league.tables.item.libs'] = MagicMock()
    sys.modules['league.tables.reset'] = MagicMock()
    sys.modules['league.tables.response.libs'] = MagicMock()
    sys.modules['league.tables.response.types'] = MagicMock()
    sys.modules['league.tables.sessions'] = MagicMock()
    sys.modules['league.tables.users'] = MagicMock()
    sys.modules['league.validate'] = MagicMock()


@pytest.fixture(scope='function')
def aws_credentials():
    """Mocked AWS Credentials for moto."""
    os.environ['AWS_ACCESS_KEY_ID'] = 'testing'
    os.environ['AWS_SECRET_ACCESS_KEY'] = 'testing'
    os.environ['AWS_SECURITY_TOKEN'] = 'testing'
    os.environ['AWS_SESSION_TOKEN'] = 'testing'
    os.environ['AWS_DEFAULT_REGION'] = 'us-east-1'


@pytest.fixture(scope='function')
def frozen_date():
    yield datetime(
        year=2026,
        month=4,
        day=20,
        hour=15,
        minute=6,
        second=3,
        microsecond=100,
        tzinfo=UTC,
    )


__all__ = [
    'reset_client_error',
    'reset_item',
    'reset_table',
    'reset_table_client_error',
    'reset_table_with_item',
    'session_item',
    'sessions_client_error',
    'sessions_table',
    'sessions_table_client_error',
    'sessions_table_with_session',
    'test_user',
    'users_client_error',
    'users_table',
    'users_table_client_error',
    'users_table_with_user',
]
