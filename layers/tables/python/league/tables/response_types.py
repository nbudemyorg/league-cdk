from typing import Any, TypedDict

from types_boto3_dynamodb.type_defs import ConsumedCapacityTypeDef


class PutItemSuccess(TypedDict):
    success: bool
    attributes: dict[str, Any] | None
    consumed_capacity: ConsumedCapacityTypeDef | None


class GetItemSuccess(TypedDict):
    success: bool
    item: dict[str, Any] | None
    consumed_capacity: ConsumedCapacityTypeDef | None


class UpdateItemSuccess(TypedDict):
    success: bool
    attributes: dict[str, Any] | None
    consumed_capacity: ConsumedCapacityTypeDef | None


class Failure(TypedDict):
    success: bool
    error_code: str
    error_message: str


PutResult = PutItemSuccess | Failure
GetResult = GetItemSuccess | Failure
UpdateResult = UpdateItemSuccess | Failure
