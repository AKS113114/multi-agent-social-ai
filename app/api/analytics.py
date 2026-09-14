from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database.database import get_db
from app.orchestration.workflow import WorkflowEngine
from app.simulator.platform import MockPlatformService

router = APIRouter(prefix="/api/analytics", tags=["Analytics"])

@router.get("/summary/{campaign_id}/{week_number}")
def get_week_analytics(campaign_id: str, week_number: int, db: Session = Depends(get_db)):
    summary = MockPlatformService.get_campaign_analytics_summary(db, campaign_id, week_number)
    return summary

@router.get("/comparison/{campaign_id}")
def get_week_comparison(campaign_id: str, db: Session = Depends(get_db)):
    comp = WorkflowEngine.compute_week_comparison(db, campaign_id)
    return comp
