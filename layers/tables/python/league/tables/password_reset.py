from botocore.exceptions import ClientError
from league.tables.item_types import ResetItem
from league.tables.response_libs import (
    get_item_response,
    item_exception_response,
    put_item_response,
)
from league.tables.response_types import GetResult, PutResult
from types_boto3_dynamodb.service_resource import Table


def get_reset_item(table: Table, reset_id: str) -> GetResult:
    """Returns item for Reset ID if it exists in the Reset table."""

    try:
        response = table.get_item(Key={'reset_id': reset_id})
        return get_item_response(response)

    except ClientError as e:
        return item_exception_response(e)


def put_reset_item(table: Table, item: ResetItem) -> PutResult:
    """Put new reset item in the Reset Table"""

    try:
        response = table.put_item(Item=item)
        return put_item_response(response)

    except ClientError as e:
        return item_exception_response(e)
