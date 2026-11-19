
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from app.tools import CRMTool, OrderTool

app = FastAPI(title="End-to-End Testing API")

crm_tool = CRMTool()
order_tool = OrderTool()

documents = {}


class DocumentRequest(BaseModel):
    filename: str
    content: str


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1)


class EmailRequest(BaseModel):
    topic: str
    tone: str = "formal"


@app.get("/")
def home():
    return {"message": "End-to-End Testing API is running"}


@app.post("/documents")
def upload_document(request: DocumentRequest):
    if not request.content.strip():
        raise HTTPException(status_code=400, detail="Document content cannot be empty.")

    documents[request.filename] = request.content

    return {
        "success": True,
        "filename": request.filename
    }


@app.post("/chat")
def chat(request: ChatRequest):
    message = request.message.lower()

    
    if "customer" in message or "crm" in message:
        import re

        match = re.search(r"\bC\d+\b", message, re.IGNORECASE)

        if not match:
            return {
                "answer": {
                    "success": False,
                    "message": "Customer ID is required."
                },
                "tools_used": ["CRMTool"]
            }

        customer_id = match.group(0).upper()
        return {
            "answer": crm_tool.get_customer(customer_id),
            "tools_used": ["CRMTool"]
        }

    if "order" in message:
        order_id = "O102" if "o102" in message else "O101"
        return {
            "answer": order_tool.get_order(order_id),
            "tools_used": ["OrderTool"]
        }

    if any(word in message for word in ["document", "policy", "report"]):
        if not documents:
            return {
                "answer": "Please upload a document first.",
                "tools_used": ["DocumentSearch"]
            }

       
        question_words = set(message.split())

        best_document = None
        best_score = 0

        for filename, content in documents.items():
            searchable_text = f"{filename} {content}".lower()
            score = sum(
                1 for word in question_words
                if len(word) > 2 and word in searchable_text
            )

            if score > best_score:
                best_score = score
                best_document = content

        if best_document is None:
            return {
                "answer": "I cannot find this information in the available documents.",
                "tools_used": ["DocumentSearch"]
            }

        return {
            "answer": best_document[:500],
            "tools_used": ["DocumentSearch"]
        }

    return {
        "answer": "I cannot find this information in the available data.",
        "tools_used": []
    }


@app.post("/draft-email")
def draft_email(request: EmailRequest):
    if request.tone not in ["formal", "friendly"]:
        raise HTTPException(status_code=400, detail="Tone must be formal or friendly.")

    greeting = "Dear Customer," if request.tone == "formal" else "Hello!"

    return {
        "subject": f"Regarding {request.topic}",
        "body": (
            f"{greeting}\n\n"
            f"We are writing to discuss {request.topic}.\n\n"
            "Please contact us if you need further assistance.\n\n"
            "Best regards,\nSupport Team"
        ),
        "tools_used": ["EmailDraft"]
    }

def test_unknown_customer_id():
    response = client.post(
        "/chat",
        json={"message": "Show customer C999 details."}
    )

    assert response.status_code == 200
    assert response.json()["answer"]["success"] is False
    assert response.json()["answer"]["message"] == "Customer not found."