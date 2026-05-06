from typing import NotRequired, TypedDict


class UserItem(TypedDict):
    player_id: str
    password: str
    email: str
    reset_id: NotRequired[str]


class SessionItem(TypedDict):
    player_id: str
    session_id: str
    expiry: str
    ttl: int


class ResetItem(TypedDict):
    reset_id: str
    player_id: str
    expiry: str
    ttl: int
