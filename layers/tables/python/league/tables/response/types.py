from typing import Any, TypedDict

from types_boto3_dynamodb.type_defs import ConsumedCapacityTypeDef


class PutItemSuccess(TypedDict):
    success: bool
    attributes: dict[str, Any]
    consumed_capacity: ConsumedCapacityTypeDef


class GetItemSuccess(TypedDict):
    success: bool
    item: dict[str, Any]
    consumed_capacity: ConsumedCapacityTypeDef


class UpdateItemSuccess(TypedDict):
    success: bool
    attributes: dict[str, Any]
    consumed_capacity: ConsumedCapacityTypeDef


class Failure(TypedDict):
    success: bool
    error_code: str
    error_message: str


class DeleteItemSuccess(TypedDict):
    success: bool
    attributes: dict[str, Any]
    consumed_capacity: ConsumedCapacityTypeDef


PutResult = PutItemSuccess | Failure
GetResult = GetItemSuccess | Failure
DeleteResult = DeleteItemSuccess | Failure
UpdateResult = UpdateItemSuccess | Failure
