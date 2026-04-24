from typing import Any, NotRequired, TypedDict


class PutItemSuccess(TypedDict):
    success: bool
    attributes: dict[str, Any] | None
    consumed_capacity: dict[str, Any] | None

class GetItemSuccess(TypedDict):
    success: bool
    item: dict[str, Any] | None
    consumed_capacity: dict[str, Any] | None

class Failure(TypedDict):
    success: bool
    error_code: str
    error_message: str

PutResult = PutItemSuccess | Failure
GetResult = GetItemSuccess | Failure