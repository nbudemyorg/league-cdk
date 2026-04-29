from collections.abc import Mapping
from typing import Any, cast

from botocore.exceptions import ClientError
from league.tables.item_types import UserItem
from league.tables.response_libs import (
    get_item_response,
    item_exception_response,
    put_item_response,
    update_item_response,
)
from league.tables.response_types import GetResult, GetItemSuccess, PutResult
from types_boto3_dynamodb.service_resource import Table


def get_users_item(table: Table, supplied_id: str) -> GetResult:
    """Returns item for Player ID if it exists in the Users table."""

    try:
        response = table.get_item(Key={'player_id': supplied_id})
        return get_item_response(response)

    except ClientError as e:
        return item_exception_response(e)


def put_users_item(table: Table, item: UserItem) -> PutResult:

    try:
        response = table.put_item(
            Item=cast('Mapping[str, Any]', item),
            ConditionExpression='attribute_not_exists(player_id)'
        )
        return put_item_response(response)

    except ClientError as e:
        return item_exception_response(e)


def update_users_item(table: Table, player_id: str, token: str) -> PutResult:

    try:
        response = table.update_item(
            Key={'player_id': player_id},
            UpdateExpression='SET #rid = :val',
            ExpressionAttributeNames={'#rid': 'reset_id'},
            ExpressionAttributeValues={':val': token},
            ReturnValues='UPDATED_NEW',
        )
        return update_item_response(response)

    except ClientError as e:
        return item_exception_response(e)
