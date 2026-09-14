from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database.database import get_db
from app.orchestration.state import MessageBus
from app.llm.ollama_client import ollama_client

router = APIRouter(prefix="/api/agents", tags=["Agents"])

@router.get("/trace/{campaign_id}")
def get_campaign_trace(campaign_id: str, db: Session = Depends(get_db)):
    traces = MessageBus.get_campaign_traces(db, campaign_id)
    return [
        {
            "id": t.id,
            "agent": t.agent,
            "action": t.action,
            "input_summary": t.input_summary,
            "output_summary": t.output_summary,
            "status": t.status,
            "revision_count": t.revision_count,
            "handoff_to": t.handoff_to,
            "timestamp": t.timestamp.isoformat() if t.timestamp else None
        } for t in traces
    ]

@router.get("/messages/{campaign_id}")
def get_campaign_messages(campaign_id: str, db: Session = Depends(get_db)):
    messages = MessageBus.get_campaign_messages(db, campaign_id)
    return [
        {
            "id": m.id,
            "sender": m.sender,
            "recipient": m.recipient,
            "message_type": m.message_type,
            "payload": m.payload,
            "status": m.status,
            "timestamp": m.timestamp.isoformat() if m.timestamp else None
        } for m in messages
    ]

@router.get("/status")
def get_ollama_status():
    return ollama_client.health_check()
