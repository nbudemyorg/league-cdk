from botocore.exceptions import ClientError
from item_types import PasswordResetItem
from response_libs import (
    get_item_response,
    item_exception_response,
    put_item_response,
)
from response_types import GetResult, PutResult
from types_boto3_dynamodb.service_resource import Table


def get_reset_item(table: Table, reset_id: str) -> GetResult:
    """Returns item for Player ID if it exists in the Users table."""

    try:
        response = table.get_item(Key={'reset_id': reset_id})
        return get_item_response(response)

    except ClientError as e:
        return item_exception_response(e)


def put_reset_item(table: Table, item: PasswordResetItem) -> PutResult:

    try:
        response = table.put_item(Item=item)
        return put_item_response(response)

    except ClientError as e:
        return item_exception_response(e)
