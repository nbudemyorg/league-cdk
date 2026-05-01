import sys
from typing import Any

import pytest
from botocore.exceptions import ClientError


@pytest.fixture
def mock_get_response_with_item():
    yield {
        'ConsumedCapacity': {'CapacityUnits': 1},
        'Item': {'data': 'found'},
    }


@pytest.fixture
def mock_get_response_no_item():
    yield {
        'ConsumedCapacity': {'CapacityUnits': 2},
    }


@pytest.fixture
def mock_put_response():
    yield {
        'Attributes': {'S': 'Attributes'},
        'ConsumedCapacity': {'CapacityUnits': 3},
    }


@pytest.fixture
def mock_update_response():
    yield {
        'Attributes': {'S': 'Attributes'},
        'ConsumedCapacity': {'CapacityUnits': 4},
    }


@pytest.mark.response_libs
def test_mocked_modules(mock_league_tables_layer: None) -> None:
    assert 'league.tables.item.libs' in sys.modules
    assert 'league.tables.item.types' in sys.modules
    assert 'league.tables.password_reset' in sys.modules
    assert 'league.tables.response.libs' in sys.modules
    assert 'league.tables.response.types' in sys.modules
    assert 'league.tables.sessions' in sys.modules
    assert 'league.tables.users' in sys.modules


@pytest.mark.response_libs
def test_get_item_response(
    mock_get_response_with_item: dict[str, Any],
    mock_get_response_no_item: dict[str, Any],
) -> None:

    from layers.tables.python.league.tables.response.libs import (
        get_item_response,
    )

    response = get_item_response(mock_get_response_with_item)
    item = mock_get_response_with_item['Item']
    consumed_capacity = mock_get_response_with_item['ConsumedCapacity']

    assert response['success'] is True
    assert response['item'] == item
    assert response['consumed_capacity'] == consumed_capacity

    response = get_item_response(mock_get_response_no_item)
    consumed_capacity = mock_get_response_no_item['ConsumedCapacity']

    assert response['success'] is True
    assert response['item'] == {}
    assert response['consumed_capacity'] == consumed_capacity


@pytest.mark.response_libs
def test_put_item_response(mock_put_response: dict[str, Any]) -> None:
    from layers.tables.python.league.tables.response.libs import (
        put_item_response,
    )

    response = put_item_response(mock_put_response)
    attributes = mock_put_response['Attributes']
    consumed_capacity = mock_put_response['ConsumedCapacity']

    assert response['success'] is True
    assert response['attributes'] == attributes
    assert response['consumed_capacity'] == consumed_capacity


@pytest.mark.response_libs
def test_update_item_response(mock_update_response) -> None:
    from layers.tables.python.league.tables.response.libs import (
        update_item_response,
    )

    response = update_item_response(mock_update_response)
    attributes = mock_update_response['Attributes']
    consumed_capacity = mock_update_response['ConsumedCapacity']

    assert response['success'] is True
    assert response['attributes'] == attributes
    assert response['consumed_capacity'] == consumed_capacity


@pytest.mark.response_libs
def test_item_exception_response(client_error_object: dict[str, Any]) -> None:
    from layers.tables.python.league.tables.response.libs import (
        item_exception_response,
    )

    client_error = ClientError(client_error_object, 'PutItem')

    response = item_exception_response(client_error)

    assert response['success'] is False
    assert response['error_code'] == client_error_object['Error']['Code']
    assert response['error_message'] == client_error_object['Error']['Message']
