import pytest
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database.database import Base
from app.services.campaign_service import CampaignService
from app.orchestration.workflow import WorkflowEngine

@pytest.fixture
def db_session():
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = TestingSessionLocal()
    yield session
    session.close()

def run_workflow_test(db_session):
    print("\n========================================================================", flush=True)
    print("STARTING END-TO-END WORKFLOW INTEGRATION TEST", flush=True)
    print("========================================================================", flush=True)

    brief = (
        "We are launching a budget espresso machine for students. "
        "Run a two-week awareness campaign across our three channels, "
        "target price-sensitive 18–25 year olds, keep the tone playful, don't over-promise."
    )
    
    # 1. Create Campaign
    print("\n[STEP 1] Creating Campaign from Human Brief...", flush=True)
    campaign = CampaignService.create_campaign(db_session, title="E2E Workflow Test Campaign", human_brief=brief)
    assert campaign.id is not None
    assert campaign.status == "DRAFT"
    print(f"-> Campaign Created: ID={campaign.id}, Status={campaign.status}", flush=True)

    # 2. Run Week 1 Pipeline (Strategy -> Content -> Creative -> Compliance)
    print("\n[STEP 2] Executing Week 1 Pipeline (Strategy -> Content -> Creative -> Compliance Loop)...", flush=True)
    w1_res = CampaignService.run_week1_pipeline(db_session, campaign.id)
    db_session.refresh(campaign)
    assert campaign.status == "HUMAN_REVIEW"
    assert len(campaign.posts) > 0
    print(f"-> Week 1 Pipeline Complete: Status={campaign.status}, Posts Generated={len(campaign.posts)}", flush=True)
    print(f"-> Week 1 Strategy Pillars: {campaign.content_pillars}", flush=True)

    # 3. Human Approval Gate
    print("\n[STEP 3] Human Approval Gate Interception...", flush=True)
    print(f"-> Human reviewing {len(campaign.posts)} posts for Week 1...", flush=True)
    WorkflowEngine.approve_entire_campaign(db_session, campaign.id)
    db_session.refresh(campaign)
    assert campaign.status == "APPROVED"
    print(f"-> Human Gate Passed: Campaign Status={campaign.status}", flush=True)

    # 4. Publish & Simulate Week 1
    print("\n[STEP 4] Publishing to Mock Platform & Simulating Week 1 Engagement + Comments...", flush=True)
    pub_res = CampaignService.publish_week_and_simulate(db_session, campaign.id, week_number=1)
    db_session.refresh(campaign)
    assert campaign.status == "IMPROVEMENT"
    assert campaign.week1_analytics_report is not None
    assert len(campaign.week2_recommendations) > 0

    print("\n------------------------------------------------------------------------", flush=True)
    print("WEEK 1 ANALYTICS DISCOVERED PATTERNS & RECOMMENDATIONS:", flush=True)
    print("------------------------------------------------------------------------", flush=True)
    recs = campaign.week2_recommendations
    for idx, rec in enumerate(recs, 1):
        print(f"Recommendation #{idx} [{rec.get('channel')}/{rec.get('category')}]:", flush=True)
        print(f"  Observation : {rec.get('observation', 'N/A')}", flush=True)
        print(f"  Evidence    : {rec.get('evidence', 'N/A')}", flush=True)
        print(f"  Hypothesis  : {rec.get('hypothesis', 'N/A')}", flush=True)
        print(f"  Confidence  : {rec.get('confidence', 'N/A')}", flush=True)
        print(f"  Instruction : {rec.get('recommendation', 'N/A')}", flush=True)
    print("------------------------------------------------------------------------", flush=True)

    # 5. Run Week 2 Strategy Improvement Loop (Analytics Recommendations -> Strategy -> Content -> Compliance)
    print("\n[STEP 5] Executing Week 2 Closed Feedback Loop...", flush=True)
    print("-> Passing Week 1 Recommendations directly into Strategy Agent for Week 2...", flush=True)
    w2_res = CampaignService.run_week2_pipeline(db_session, campaign.id)
    db_session.refresh(campaign)
    assert campaign.week_number == 2
    assert campaign.status == "HUMAN_REVIEW"
    assert campaign.week2_strategy_adjustments is not None
    print(f"-> Week 2 Pipeline Complete: Status={campaign.status}", flush=True)

    print("\n------------------------------------------------------------------------", flush=True)
    print("WEEK 2 REVISED STRATEGY OUTPUT (Consuming Week 1 Feedback):", flush=True)
    print("------------------------------------------------------------------------", flush=True)
    print(f"Week 2 Objective: {campaign.week2_strategy_adjustments.get('objective')}", flush=True)
    print(f"Week 2 Cadence  : {campaign.week2_strategy_adjustments.get('posting_cadence')}", flush=True)
    print(f"Week 2 Hypotheses: {campaign.week2_strategy_adjustments.get('strategic_hypotheses')}", flush=True)
    print("------------------------------------------------------------------------", flush=True)

    # 6. Approve & Publish Week 2
    print("\n[STEP 6] Human Approving Week 2 Campaign & Publishing to Mock Platform...", flush=True)
    WorkflowEngine.approve_entire_campaign(db_session, campaign.id)
    CampaignService.publish_week_and_simulate(db_session, campaign.id, week_number=2)
    db_session.refresh(campaign)

    # 7. Verify Week 1 vs Week 2 Comparison
    print("\n[STEP 7] Computing Week 1 vs Week 2 Performance Deltas...", flush=True)
    comp = WorkflowEngine.compute_week_comparison(db_session, campaign.id)
    
    print("\n========================================================================", flush=True)
    print("WEEK 1 VS WEEK 2 PERFORMANCE DELTA COMPARISON RESULTS:", flush=True)
    print("========================================================================", flush=True)
    print(f"Total Posts         | W1: {comp['week1']['total_posts']} -> W2: {comp['week2']['total_posts']}", flush=True)
    print(f"Impressions         | W1: {comp['deltas']['impressions']['w1']} -> W2: {comp['deltas']['impressions']['w2']} ({comp['deltas']['impressions']['pct']})", flush=True)
    print(f"Engagement Rate     | W1: {comp['deltas']['avg_engagement_rate']['w1']} -> W2: {comp['deltas']['avg_engagement_rate']['w2']} ({comp['deltas']['avg_engagement_rate']['pct']})", flush=True)
    print(f"Likes               | W1: {comp['deltas']['likes']['w1']} -> W2: {comp['deltas']['likes']['w2']} ({comp['deltas']['likes']['pct']})", flush=True)
    print(f"Comments            | W1: {comp['deltas']['comments']['w1']} -> W2: {comp['deltas']['comments']['w2']} ({comp['deltas']['comments']['pct']})", flush=True)
    print(f"Shares              | W1: {comp['deltas']['shares']['w1']} -> W2: {comp['deltas']['shares']['w2']} ({comp['deltas']['shares']['pct']})", flush=True)
    print(f"Saves               | W1: {comp['deltas']['saves']['w1']} -> W2: {comp['deltas']['saves']['w2']} ({comp['deltas']['saves']['pct']})", flush=True)
    print(f"Clicks              | W1: {comp['deltas']['clicks']['w1']} -> W2: {comp['deltas']['clicks']['w2']} ({comp['deltas']['clicks']['pct']})", flush=True)
    print(f"Follower Delta      | W1: {comp['deltas']['follower_delta']['w1']} -> W2: {comp['deltas']['follower_delta']['w2']} ({comp['deltas']['follower_delta']['pct']})", flush=True)
    print("========================================================================\n", flush=True)

    # AUTOMATED CADENCE & INTEGRITY ASSERTIONS
    assert "week1" in comp
    assert "week2" in comp
    assert "deltas" in comp
    # Assert Cadence Consistency: Strategy Cadence == Scheduled Posts == Published Posts == Analytics Data (3 posts per week demo scope)
    assert comp["week1"]["total_posts"] == 3
    assert comp["week2"]["total_posts"] == 3
    assert len(campaign.posts) == 6  # 3 posts in Week 1 + 3 posts in Week 2
    print("SUCCESS: End-to-End Workflow Integration Test Completed Successfully & All Cadence Assertions Passed!", flush=True)

def test_end_to_end_campaign_workflow(db_session):
    run_workflow_test(db_session)

if __name__ == "__main__":
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = TestingSessionLocal()
    try:
        run_workflow_test(session)
    finally:
        session.close()
