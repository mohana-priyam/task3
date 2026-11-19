import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


# 1. DOCUMENT QUESTION: Company policy
def test_document_policy_question():
    upload = client.post(
        "/documents",
        json={
            "filename": "policy.txt",
            "content": "Employees receive 20 days of annual leave."
        }
    )
    assert upload.status_code == 200

    response = client.post(
        "/chat",
        json={"message": "What does the company policy say?"}
    )

    assert response.status_code == 200
    assert "20 days" in response.json()["answer"]
    assert "DocumentSearch" in response.json()["tools_used"]


# 2. DOCUMENT QUESTION: Annual leave
def test_document_annual_leave_question():
    client.post(
        "/documents",
        json={
            "filename": "leave.txt",
            "content": "Employees receive 20 days of annual leave."
        }
    )

    response = client.post(
        "/chat",
        json={"message": "Tell me about the leave document."}
    )

    assert response.status_code == 200
    assert "20 days" in response.json()["answer"]


# 3. DOCUMENT QUESTION: Report
def test_document_report_question():
    client.post(
        "/documents",
        json={
            "filename": "report.txt",
            "content": "The sales report shows revenue of 500000."
        }
    )

    response = client.post(
        "/chat",
        json={"message": "Summarize the sales report."}
    )

    assert response.status_code == 200
    assert "500000" in response.json()["answer"]


# 4. UNANSWERABLE QUESTION: Unknown information
def test_unanswerable_weather_question():
    response = client.post(
        "/chat",
        json={"message": "What is the weather on Mars?"}
    )

    assert response.status_code == 200
    assert "cannot find" in response.json()["answer"].lower()
    assert response.json()["tools_used"] == []


# 5. UNANSWERABLE QUESTION: Unknown company information
def test_unanswerable_question():
    response = client.post(
        "/chat",
        json={"message": "What is the CEO's favourite colour?"}
    )

    assert response.status_code == 200
    assert "cannot find" in response.json()["answer"].lower()
    assert response.json()["tools_used"] == []


# 6. CRM QUESTION: Customer C101
def test_crm_customer_c101():
    response = client.post(
        "/chat",
        json={"message": "Show customer C101 details."}
    )

    assert response.status_code == 200
    assert response.json()["answer"]["success"] is True
    assert response.json()["answer"]["data"]["name"] == "Arun Kumar"
    assert "CRMTool" in response.json()["tools_used"]


# 7. CRM QUESTION: Customer C102
def test_crm_customer_c102():
    response = client.post(
        "/chat",
        json={"message": "Show customer C102 details."}
    )

    assert response.status_code == 200
    assert response.json()["answer"]["success"] is True
    assert response.json()["answer"]["data"]["name"] == "Priya Sharma"


# 8. ORDER QUESTION: Order O101
def test_order_o101():
    response = client.post(
        "/chat",
        json={"message": "Check order O101 status."}
    )

    assert response.status_code == 200
    assert response.json()["answer"]["success"] is True
    assert response.json()["answer"]["data"]["status"] == "Shipped"
    assert "OrderTool" in response.json()["tools_used"]


# 9. ORDER QUESTION: Order O102
def test_order_o102():
    response = client.post(
        "/chat",
        json={"message": "Check order O102 status."}
    )

    assert response.status_code == 200
    assert response.json()["answer"]["success"] is True
    assert response.json()["answer"]["data"]["status"] == "Delivered"


# 10. EMAIL DRAFT
def test_email_draft():
    response = client.post(
        "/draft-email",
        json={
            "topic": "Order delivery update",
            "tone": "formal"
        }
    )

    assert response.status_code == 200
    assert "Order delivery update" in response.json()["subject"]
    assert "Dear Customer" in response.json()["body"]
    assert "EmailDraft" in response.json()["tools_used"]

# 11. UNKNOWN CUSTOMER ID
def test_unknown_customer_id():
    response = client.post(
        "/chat",
        json={"message": "Show customer C999 details."}
    )

    assert response.status_code == 200
    assert response.json()["answer"]["success"] is False
    assert response.json()["answer"]["message"] == "Customer not found."