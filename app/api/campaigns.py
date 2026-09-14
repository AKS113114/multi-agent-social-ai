from typing import Dict, Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.database.database import get_db
from app.services.campaign_service import CampaignService
from app.orchestration.workflow import WorkflowEngine

router = APIRouter(prefix="/api/campaigns", tags=["Campaigns"])

class CreateCampaignRequest(BaseModel):
    title: str
    human_brief: str

@router.post("")
def create_campaign(req: CreateCampaignRequest, db: Session = Depends(get_db)):
    campaign = CampaignService.create_campaign(db, title=req.title, human_brief=req.human_brief)
    return {"status": "success", "campaign_id": campaign.id, "title": campaign.title}

@router.get("")
def list_campaigns(db: Session = Depends(get_db)):
    campaigns = CampaignService.list_all_campaigns(db)
    return [
        {
            "id": c.id,
            "title": c.title,
            "human_brief": c.human_brief,
            "status": c.status,
            "week_number": c.week_number,
            "created_at": c.created_at.isoformat() if c.created_at else None
        } for c in campaigns
    ]

@router.get("/{campaign_id}")
def get_campaign(campaign_id: str, db: Session = Depends(get_db)):
    campaign = CampaignService.get_campaign_full(db, campaign_id)
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    
    posts = [
        {
            "id": p.id,
            "week_number": p.week_number,
            "channel": p.channel,
            "format": p.format,
            "scheduled_time": p.scheduled_time,
            "copy": p.copy,
            "hook": p.hook,
            "cta": p.cta,
            "hashtags": p.hashtags,
            "content_pillar": p.content_pillar,
            "compliance_status": p.compliance_status,
            "human_approval_status": p.human_approval_status,
            "human_feedback": p.human_feedback,
            "is_published": p.is_published,
            "creative_brief": {
                "visual_concept": p.creative_brief.visual_concept,
                "asset_type": p.creative_brief.asset_type,
                "visual_hook": p.creative_brief.visual_hook,
                "scene_description": p.creative_brief.scene_description,
                "on_screen_text": p.creative_brief.on_screen_text,
                "brand_direction": p.creative_brief.brand_direction
            } if p.creative_brief else None,
            "compliance_reviews": [
                {
                    "attempt": r.attempt_number,
                    "approved": r.approved,
                    "score": r.score,
                    "issues": r.issues,
                    "required_changes": r.required_changes,
                    "reasoning": r.reasoning
                } for r in p.compliance_reviews
            ]
        } for p in campaign.posts
    ]

    return {
        "id": campaign.id,
        "title": campaign.title,
        "human_brief": campaign.human_brief,
        "status": campaign.status,
        "week_number": campaign.week_number,
        "target_audience": campaign.target_audience,
        "channels": campaign.channels,
        "duration_days": campaign.duration_days,
        "content_pillars": campaign.content_pillars,
        "posting_cadence": campaign.posting_cadence,
        "kpis": campaign.kpis,
        "strategic_hypotheses": campaign.strategic_hypotheses,
        "week1_analytics_report": campaign.week1_analytics_report,
        "week2_recommendations": campaign.week2_recommendations,
        "week2_strategy_adjustments": campaign.week2_strategy_adjustments,
        "posts": posts
    }

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from app.database.database import get_db, SessionLocal

def _run_week1_bg(campaign_id: str):
    db = SessionLocal()
    try:
        CampaignService.run_week1_pipeline(db, campaign_id)
    except Exception as e:
        print(f"Background Week 1 error: {e}")
    finally:
        db.close()

def _run_week2_bg(campaign_id: str):
    db = SessionLocal()
    try:
        CampaignService.run_week2_pipeline(db, campaign_id)
    except Exception as e:
        print(f"Background Week 2 error: {e}")
    finally:
        db.close()

@router.post("/{campaign_id}/run-week1")
def run_week1(campaign_id: str, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    background_tasks.add_task(_run_week1_bg, campaign_id)
    return {"status": "processing", "message": "Week 1 pipeline started in background", "campaign_id": campaign_id}

@router.post("/{campaign_id}/approve-campaign")
def approve_campaign(campaign_id: str, db: Session = Depends(get_db)):
    campaign = WorkflowEngine.approve_entire_campaign(db, campaign_id)
    return {"status": "approved", "campaign_id": campaign.id, "new_status": campaign.status}

@router.post("/{campaign_id}/publish-week")
def publish_week(campaign_id: str, week_number: int = 1, db: Session = Depends(get_db)):
    res = CampaignService.publish_week_and_simulate(db, campaign_id, week_number)
    return res

@router.post("/{campaign_id}/run-week2")
def run_week2(campaign_id: str, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    background_tasks.add_task(_run_week2_bg, campaign_id)
    return {"status": "processing", "message": "Week 2 pipeline started in background", "campaign_id": campaign_id}
