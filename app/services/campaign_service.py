import uuid
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from app.database.models import CampaignModel, PostModel, AgentMessageModel, AgentTraceModel, PlatformPostModel, PlatformCommentModel
from app.agents.orchestrator import OrchestratorAgent
from app.orchestration.workflow import WorkflowEngine

class CampaignService:
    @staticmethod
    def create_campaign(db: Session, title: str, human_brief: str) -> CampaignModel:
        campaign_id = f"cmp_{uuid.uuid4().hex[:8]}"
        campaign = CampaignModel(
            id=campaign_id,
            title=title,
            human_brief=human_brief,
            status="DRAFT",
            week_number=1
        )
        db.add(campaign)
        db.commit()
        db.refresh(campaign)
        return campaign

    @staticmethod
    def run_week1_pipeline(db: Session, campaign_id: str) -> Dict[str, Any]:
        orchestrator = OrchestratorAgent()
        return orchestrator.run_campaign_week1(db, campaign_id)

    @staticmethod
    def publish_week_and_simulate(db: Session, campaign_id: str, week_number: int = 1) -> Dict[str, Any]:
        orchestrator = OrchestratorAgent()
        return orchestrator.publish_and_simulate_week(db, campaign_id, week_number)

    @staticmethod
    def run_week2_pipeline(db: Session, campaign_id: str) -> Dict[str, Any]:
        orchestrator = OrchestratorAgent()
        return orchestrator.run_campaign_week2(db, campaign_id)

    @staticmethod
    def get_campaign_full(db: Session, campaign_id: str) -> Optional[CampaignModel]:
        return db.query(CampaignModel).filter(CampaignModel.id == campaign_id).first()

    @staticmethod
    def list_all_campaigns(db: Session) -> List[CampaignModel]:
        return db.query(CampaignModel).order_by(CampaignModel.created_at.desc()).all()
