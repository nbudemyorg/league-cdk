from botocore.exceptions import ClientError
from league.tables.response_types import GetResult, PutResult
from types_boto3_dynamodb.type_defs import (
    GetItemOutputTableTypeDef,
    PutItemOutputTableTypeDef,
)


def get_item_response(response: GetItemOutputTableTypeDef) -> GetResult:
    consumed = response.get('ConsumedCapacity', {})
    item = response.get('Item', {})
    return {
        'success': True,
        'item': item,
        'consumed_capacity': consumed,
    }


def item_exception_response(err: ClientError) -> GetResult:
    error = err.response.get('Error', {})
    return {
        'success': False,
        'error_code': error.get('Code', 'ClientError'),
        'error_message': error.get('Message', str(err)),
    }


def put_item_response(response: PutItemOutputTableTypeDef) -> PutResult:
    attributes = response.get('Attributes', {})
    consumed = response.get('ConsumedCapacity', {})
    return {
        'success': True,
        'attributes': attributes,
        'consumed_capacity': consumed,
    }
