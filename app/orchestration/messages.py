import uuid
from datetime import datetime
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field

class AgentMessage(BaseModel):
    message_id: str = Field(default_factory=lambda: f"msg_{uuid.uuid4().hex[:8]}")
    campaign_id: str
    sender: str # e.g. Orchestrator, StrategyAgent, ContentAgent, ComplianceAgent, etc.
    recipient: str # e.g. ContentAgent, ComplianceAgent, HumanReview, etc.
    message_type: str # TASK_ASSIGNMENT, WORK_SUBMISSION, REJECTION_FEEDBACK, APPROVAL_NOTIFICATION, ANALYTICS_REPORT
    payload: Dict[str, Any]
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
    parent_message_id: Optional[str] = None
    status: str = Field(default="SENT") # SENT, DELIVERED, PROCESSED, FAILED
