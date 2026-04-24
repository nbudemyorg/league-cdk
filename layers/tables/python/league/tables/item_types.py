from typing import Any, NotRequired, TypedDict
from botocore.exceptions import ClientError
import boto3


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

class PasswordResetItem(TypedDict):
    reset_id: str
    player_id: str
    expiry: str
    ttl: int
