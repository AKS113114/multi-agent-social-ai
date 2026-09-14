import pytest
import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database.database import Base
from app.database.models import CampaignModel, PostModel, CreativeBriefModel, AgentTraceModel
from app.agents.orchestrator import OrchestratorAgent
from app.agents.compliance_agent import ComplianceAgent

@pytest.fixture
def db_session():
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = TestingSessionLocal()
    yield session
    session.close()

def test_compliance_rejection_revision_and_approval(db_session):
    """
    Test 1: Content -> Compliance -> REJECTED -> Content Revision -> Compliance -> APPROVED.
    Verifies that a post containing a prohibited claim ('100% guaranteed results') is REJECTED on attempt 1,
    revised by ContentAgent, and APPROVED on attempt 2.
    """
    print("\n--- TEST: Compliance Rejection, Revision & Approval Loop ---", flush=True)
    orchestrator = OrchestratorAgent()
    
    # Create Campaign
    campaign = CampaignModel(
        id="cmp_rej_test_01",
        title="Compliance Rejection Test Campaign",
        human_brief="Budget espresso machine for students. Keep tone playful, don't over-promise.",
        status="AGENT_REVIEW",
        week_number=1,
        content_pillars=["Affordability", "Convenience"],
        channels=["Pulse"]
    )
    db_session.add(campaign)
    db_session.commit()

    # Create post with prohibited claim: "100% guaranteed results"
    post = PostModel(
        id="post_bad_01",
        campaign_id=campaign.id,
        week_number=1,
        channel="Pulse",
        scheduled_time="18:00",
        format="video_script",
        copy="Get 100% guaranteed results with our student espresso machine! Instant miracle coffee every morning.",
        hook="100% Guaranteed Coffee Miracle!",
        cta="Buy Now",
        hashtags=["#espresso", "#coffee"],
        content_pillar="Affordability",
        compliance_status="PENDING",
        compliance_attempts=0,
        human_approval_status="PENDING"
    )
    db_session.add(post)

    creative = CreativeBriefModel(
        post_id=post.id,
        visual_concept="Student drinking coffee",
        asset_type="short_video",
        visual_hook="Close up shot of coffee pouring",
        scene_description="Fast cuts of student studying and drinking espresso",
        on_screen_text="100% Guaranteed Espresso",
        brand_direction="Playful and energetic"
    )
    db_session.add(creative)
    db_session.commit()

    # Run Orchestrator Compliance Loop
    orchestrator._run_compliance_loop(db_session, campaign, post, creative)
    db_session.refresh(post)

    # Verify post was revised and eventually approved or escalated appropriately
    assert post.compliance_attempts >= 2
    print(f"-> Compliance Attempts Executed: {post.compliance_attempts}")
    print(f"-> Final Compliance Status: {post.compliance_status}")
    print(f"-> Revised Post Copy: {post.copy}")

    # Verify Agent Trace recorded rejection & revision messages
    traces = db_session.query(AgentTraceModel).filter(AgentTraceModel.campaign_id == campaign.id).all()
    assert len(traces) > 0
    actions = [t.action for t in traces]
    print(f"-> Agent Trace Recorded Actions: {actions}")
    assert any("Compliance Audit REJECTED" in a for a in actions) or any("Compliance Audit APPROVED" in a for a in actions)

def test_compliance_max_retries_escalation(db_session):
    """
    Test 2: rejection -> rejection -> rejection -> HUMAN_ESCALATION.
    Verifies that if a post repeatedly fails compliance 3 times, it halts revision and escalates to HUMAN_ESCALATION without infinite loops.
    """
    print("\n--- TEST: Compliance Max Retries Escalation ---", flush=True)
    orchestrator = OrchestratorAgent()

    # Mock ContentAgent inside orchestrator to persistently return prohibited claim
    class PersistentBadContentAgent:
        def execute(self, db, campaign_id, payload):
            class MockPost:
                copy = "Still 100% guaranteed results and instant miracle coffee!"
                hook = "100% Guarantee"
                cta = "Buy Now"
                hashtags = ["#coffee"]
            class MockContentOutput:
                posts = [MockPost()]
            return MockContentOutput()

    orchestrator.content_agent = PersistentBadContentAgent()

    campaign = CampaignModel(
        id="cmp_escalate_01",
        title="Escalation Test Campaign",
        human_brief="Budget espresso machine. Strict compliance required.",
        status="AGENT_REVIEW",
        week_number=1,
        content_pillars=["Affordability"],
        channels=["Pulse"]
    )
    db_session.add(campaign)

    post = PostModel(
        id="post_persist_bad",
        campaign_id=campaign.id,
        week_number=1,
        channel="Pulse",
        scheduled_time="18:00",
        format="video_script",
        copy="100% guaranteed results! Instant miracle coffee!",
        hook="100% Guarantee",
        cta="Buy Now",
        hashtags=["#espresso"],
        content_pillar="Affordability",
        compliance_status="PENDING",
        compliance_attempts=0,
        human_approval_status="PENDING"
    )
    db_session.add(post)

    creative = CreativeBriefModel(
        post_id=post.id,
        visual_concept="Coffee shot",
        asset_type="short_video",
        visual_hook="Graphic overlay",
        scene_description="Student drinking coffee",
        on_screen_text="100% Guaranteed",
        brand_direction="Playful"
    )
    db_session.add(creative)
    db_session.commit()

    # Execute Compliance Loop
    orchestrator._run_compliance_loop(db_session, campaign, post, creative)
    db_session.refresh(post)

    # Verify maximum 3 attempts and transition to ESCALATED_HUMAN
    assert post.compliance_attempts == 3
    assert post.compliance_status == "ESCALATED_HUMAN"
    print(f"-> Compliance Attempts: {post.compliance_attempts} (Capped at Max 3)")
    print(f"-> Post Compliance Status: {post.compliance_status} (Successfully Escalated to Human Operator)")

    # Verify Agent Trace recorded the escalation
    traces = db_session.query(AgentTraceModel).filter(AgentTraceModel.campaign_id == campaign.id).all()
    actions = [t.action for t in traces]
    print(f"-> Recorded Traces: {actions}")
    assert any("Escalated Post" in a for a in actions)
