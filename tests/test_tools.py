from unittest.mock import Mock

import pytest

from app.tools import CRMTool, OrderTool


# CRM TOOL UNIT TESTS

def test_crm_customer_found():
    mock_client = Mock()
    mock_client.get_customer.return_value = {
        "customer_id": "C101",
        "name": "Arun Kumar",
        "status": "Active"
    }

    crm = CRMTool(client=mock_client)
    result = crm.get_customer("C101")

    assert result["success"] is True
    assert result["data"]["name"] == "Arun Kumar"
    mock_client.get_customer.assert_called_once_with("C101")


def test_crm_customer_not_found():
    mock_client = Mock()
    mock_client.get_customer.return_value = None

    crm = CRMTool(client=mock_client)
    result = crm.get_customer("C999")

    assert result["success"] is False
    assert result["message"] == "Customer not found."


def test_crm_missing_customer_id():
    crm = CRMTool(client=Mock())

    with pytest.raises(ValueError):
        crm.get_customer("")


# ORDER TOOL UNIT TESTS

def test_order_found():
    mock_client = Mock()
    mock_client.get_order.return_value = {
        "order_id": "O101",
        "product": "Laptop",
        "amount": 55000,
        "status": "Shipped"
    }

    order = OrderTool(client=mock_client)
    result = order.get_order("O101")

    assert result["success"] is True
    assert result["data"]["product"] == "Laptop"
    mock_client.get_order.assert_called_once_with("O101")


def test_order_not_found():
    mock_client = Mock()
    mock_client.get_order.return_value = None

    order = OrderTool(client=mock_client)
    result = order.get_order("O999")

    assert result["success"] is False
    assert result["message"] == "Order not found."


def test_missing_order_id():
    order = OrderTool(client=Mock())

    with pytest.raises(ValueError):
        order.get_order("")

