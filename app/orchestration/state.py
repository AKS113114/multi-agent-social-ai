from datetime import datetime
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from app.database.models import AgentMessageModel, AgentTraceModel, CampaignModel
from app.orchestration.messages import AgentMessage

class MessageBus:
    """
    Centralized Agent Message Bus and Execution Tracing for SQLite persistence.
    """
    @staticmethod
    def send_message(db: Session, message: AgentMessage) -> AgentMessageModel:
        db_msg = AgentMessageModel(
            id=message.message_id,
            campaign_id=message.campaign_id,
            sender=message.sender,
            recipient=message.recipient,
            message_type=message.message_type,
            payload=message.payload,
            timestamp=datetime.fromisoformat(message.timestamp) if isinstance(message.timestamp, str) else message.timestamp,
            parent_message_id=message.parent_message_id,
            status=message.status
        )
        db.add(db_msg)
        db.commit()
        db.refresh(db_msg)
        return db_msg

    @staticmethod
    def log_trace(
        db: Session,
        campaign_id: str,
        agent: str,
        action: str,
        input_summary: str,
        output_summary: str,
        status: str = "SUCCESS",
        revision_count: int = 0,
        handoff_to: Optional[str] = None
    ) -> AgentTraceModel:
        trace = AgentTraceModel(
            campaign_id=campaign_id,
            agent=agent,
            action=action,
            input_summary=input_summary,
            output_summary=output_summary,
            status=status,
            revision_count=revision_count,
            handoff_to=handoff_to,
            timestamp=datetime.utcnow()
        )
        db.add(trace)
        db.commit()
        db.refresh(trace)
        return trace

    @staticmethod
    def get_campaign_messages(db: Session, campaign_id: str) -> List[AgentMessageModel]:
        return db.query(AgentMessageModel).filter(
            AgentMessageModel.campaign_id == campaign_id
        ).order_by(AgentMessageModel.timestamp.asc()).all()

    @staticmethod
    def get_campaign_traces(db: Session, campaign_id: str) -> List[AgentTraceModel]:
        return db.query(AgentTraceModel).filter(
            AgentTraceModel.campaign_id == campaign_id
        ).order_by(AgentTraceModel.timestamp.asc()).all()
