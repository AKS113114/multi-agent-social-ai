import uuid
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database.database import Base
from app.database.models import CampaignModel, PostModel, CreativeBriefModel, ComplianceReviewModel
from app.agents.compliance_agent import ComplianceAgent
from app.agents.orchestrator import OrchestratorAgent
from app.orchestration.workflow import WorkflowEngine

@pytest.fixture
def db_session():
    # Use SQLite in-memory database for clean isolated unit tests
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = TestingSessionLocal()
    yield session
    session.close()

def test_compliance_pre_audit_banned_word(db_session):
    agent = ComplianceAgent()
    cmp_id = f"cmp_comp_{uuid.uuid4().hex[:6]}"
    campaign = CampaignModel(id=cmp_id, title="Test", human_brief="Test brief", status="DRAFT")
    db_session.add(campaign)
    db_session.commit()

    post_payload = {
        "channel": "Pulse",
        "format": "video_script",
        "hook": "Miracle coffee!",
        "copy": "This unit provides a 100% guarantee instant miracle coffee result overnight!",
        "cta": "Buy now",
        "hashtags": ["#coffee"]
    }

    eval_out = agent.execute(db_session, campaign.id, {
        "post": post_payload,
        "creative_brief": {"visual_concept": "Concept"},
        "campaign_brief": campaign.human_brief,
        "revision_count": 1
    })

    assert eval_out.approved is False
    assert eval_out.score <= 40.0
    assert any("guarantee" in issue.lower() or "miracle" in issue.lower() for issue in eval_out.issues)

def test_compliance_retry_cap_and_escalation(db_session):
    orchestrator = OrchestratorAgent()
    cmp_id = f"cmp_esc_{uuid.uuid4().hex[:6]}"
    campaign = CampaignModel(id=cmp_id, title="Test Escalation", human_brief="Keep tone playful, don't overpromise", status="COMPLIANCE")
    db_session.add(campaign)
    db_session.commit()

    post = PostModel(
        id=f"post_fail_{uuid.uuid4().hex[:6]}",
        campaign_id=cmp_id,
        week_number=1,
        channel="Pulse",
        format="video_script",
        copy="This coffee machine gives a 100% guarantee instant miracle health boost!",
        compliance_status="PENDING",
        compliance_attempts=0,
        human_approval_status="PENDING"
    )
    db_session.add(post)
    creative = CreativeBriefModel(
        post_id=post.id,
        visual_concept="Concept",
        asset_type="short_video"
    )
    db_session.add(creative)
    db_session.commit()

    # Run compliance loop
    orchestrator._run_compliance_loop(db_session, campaign, post, creative)

    # Must be marked as ESCALATED_HUMAN due to failed attempts
    db_session.refresh(post)
    assert post.compliance_attempts == 3
    assert post.compliance_status == "ESCALATED_HUMAN"

def test_human_approval_gate(db_session):
    cmp_id = f"cmp_gate_{uuid.uuid4().hex[:6]}"
    campaign = CampaignModel(id=cmp_id, title="Test Gate", human_brief="Brief", status="HUMAN_REVIEW")
    db_session.add(campaign)
    
    post = PostModel(
        id=f"post_gate_{uuid.uuid4().hex[:6]}",
        campaign_id=cmp_id,
        week_number=1,
        channel="Forum",
        format="Q_and_A",
        copy="Post copy for approval",
        compliance_status="APPROVED",
        human_approval_status="PENDING"
    )
    db_session.add(post)
    db_session.commit()

    # Approve individual post
    WorkflowEngine.approve_human_post(db_session, post.id, action="APPROVE")
    db_session.refresh(post)
    assert post.human_approval_status == "APPROVED"

    # Approve campaign
    WorkflowEngine.approve_entire_campaign(db_session, cmp_id)
    db_session.refresh(campaign)
    assert campaign.status == "APPROVED"
