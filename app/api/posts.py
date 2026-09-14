from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.database.database import get_db
from app.orchestration.workflow import WorkflowEngine

router = APIRouter(prefix="/api/posts", tags=["Posts"])

class PostApprovalRequest(BaseModel):
    action: str # APPROVE, REJECT, REVISION
    feedback: Optional[str] = None

@router.post("/{post_id}/approve")
def approve_post_action(post_id: str, req: PostApprovalRequest, db: Session = Depends(get_db)):
    post = WorkflowEngine.approve_human_post(db, post_id, action=req.action, feedback=req.feedback)
    return {"status": "success", "post_id": post.id, "human_approval_status": post.human_approval_status}
