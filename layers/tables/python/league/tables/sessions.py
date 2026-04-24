from botocore.exceptions import ClientError
from league.tables.item_types import SessionItem
from league.tables.response_libs import (
    get_item_response,
    item_exception_response,
    put_item_response,
)
from league.tables.response_types import GetResult, PutResult
from types_boto3_dynamodb.service_resource import Table


def get_sessions_item(table: Table, player: str, session: str) -> GetResult:
    """Returns item for Player ID if it exists in the Users table."""

    try:
        response = table.get_item(
            Key={'player_id': player, 'session_id': session},
            AttributesToGet=['expiry'],
        )
        return get_item_response(response)

    except ClientError as e:
        return item_exception_response(e)


def put_sessions_item(table: Table, item: SessionItem) -> PutResult:

    try:
        response = table.put_item(Item=item)
        return put_item_response(response)

    except ClientError as e:
        return item_exception_response(e)
