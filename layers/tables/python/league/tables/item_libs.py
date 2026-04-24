from datetime import UTC, datetime, timedelta
from uuid import uuid4

from league.tables.item_types import SessionItem, UserItem

COOKIE_MAX_AGE = 86_400  #  24 * 60 * 60 seconds (1 Day)
ADD_TTL = 60


def create_session_item(supplied_id: str) -> SessionItem:
    """Creates a new session item for given player_id"""
    session_id = str(uuid4())

    now = datetime.now(UTC)

    session_expiry = now + timedelta(seconds=COOKIE_MAX_AGE)
    item_ttl = int(session_expiry.timestamp() + ADD_TTL)

    return {
        'player_id': supplied_id,
        'session_id': session_id,
        'expiry': session_expiry.isoformat(),
        'ttl': item_ttl,
    }


def create_user_item(
    supplied_id: str, hashed_password: str, email: str
) -> UserItem:
    """Creates a new item holding the Player ID, hashed password and email"""

    return {
        'player_id': supplied_id,
        'password': hashed_password,
        'email': email,
    }
