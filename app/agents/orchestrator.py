import uuid
import logging
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from app.agents.base_agent import BaseAgent
from app.agents.strategy_agent import StrategyAgent
from app.agents.content_agent import ContentAgent
from app.agents.creative_agent import CreativeAgent
from app.agents.compliance_agent import ComplianceAgent
from app.agents.scheduler_agent import SchedulerAgent
from app.agents.community_agent import CommunityAgent
from app.agents.analytics_agent import AnalyticsAgent
from app.database.models import CampaignModel, PostModel, CreativeBriefModel, ComplianceReviewModel
from app.simulator.platform import MockPlatformService

logger = logging.getLogger(__name__)

class OrchestratorAgent(BaseAgent):
    """
    Chief of Staff / Orchestrator Agent.
    Manages workflow lifecycle, coordinates specialized sub-agents, enforces compliance retry caps,
    governs human approval gates, and closes the Week 1 -> Week 2 analytics improvement loop.
    """
    def __init__(self):
        super().__init__(
            name="OrchestratorAgent",
            role="Chief of Staff & System Orchestrator",
            system_prompt="You are the Chief of Staff orchestrating a team of specialized AI agents for a social media agency."
        )
        self.strategy_agent = StrategyAgent()
        self.content_agent = ContentAgent()
        self.creative_agent = CreativeAgent()
        self.compliance_agent = ComplianceAgent()
        self.scheduler_agent = SchedulerAgent()
        self.community_agent = CommunityAgent()
        self.analytics_agent = AnalyticsAgent()

    def execute(self, db: Session, campaign_id: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Orchestrator dispatch entry point.
        """
        action_type = payload.get("action", "run_week1")
        if action_type == "run_week1":
            return self.run_campaign_week1(db, campaign_id)
        elif action_type == "run_week2":
            return self.run_campaign_week2(db, campaign_id)
        else:
            raise ValueError(f"Unknown orchestrator action: {action_type}")

    def run_campaign_week1(self, db: Session, campaign_id: str) -> Dict[str, Any]:
        """
        Executes Week 1 Pipeline:
        1. Parse Brief -> Strategy Agent
        2. Content Agent -> Creative Agent -> Compliance Review Loop (Max 3 retries)
        3. Escalates to HUMAN_REVIEW state for Human Approval Gate
        """
        campaign = db.query(CampaignModel).filter(CampaignModel.id == campaign_id).first()
        if not campaign:
            raise ValueError(f"Campaign {campaign_id} not found.")

        campaign.status = "AGENT_REVIEW"
        db.commit()

        self.log_and_send(
            db=db,
            campaign_id=campaign_id,
            recipient="StrategyAgent",
            message_type="DECOMPOSE_BRIEF",
            payload={"human_brief": campaign.human_brief, "week_number": 1},
            action="Parsed human brief and instructed Strategy Agent",
            input_summary=f"Brief: {campaign.human_brief[:100]}...",
            output_summary="Decomposed requirements for Week 1"
        )

        # 1. Strategy Generation
        strategy_out = self.strategy_agent.execute(db, campaign_id, {
            "human_brief": campaign.human_brief,
            "week_number": 1
        })

        campaign.target_audience = strategy_out.target_audience.model_dump()
        campaign.channels = strategy_out.channels
        campaign.content_pillars = strategy_out.content_pillars
        campaign.posting_cadence = strategy_out.posting_cadence
        campaign.kpis = strategy_out.kpis
        campaign.strategic_hypotheses = strategy_out.strategic_hypotheses
        campaign.status = "COMPLIANCE"
        db.commit()

        # 2. Content Generation
        content_out = self.content_agent.execute(db, campaign_id, {
            "strategy": strategy_out.model_dump(),
            "week_number": 1
        })

        # Process each post through Creative & Compliance Loop
        for draft in content_out.posts:
            post_id = f"post_{uuid.uuid4().hex[:8]}"
            db_post = PostModel(
                id=post_id,
                campaign_id=campaign_id,
                week_number=1,
                channel=draft.channel,
                scheduled_time=draft.scheduled_time,
                format=draft.format,
                copy=draft.copy,
                hook=draft.hook,
                cta=draft.cta,
                hashtags=draft.hashtags,
                content_pillar=draft.content_pillar,
                compliance_status="PENDING",
                compliance_attempts=0,
                human_approval_status="PENDING"
            )
            db.add(db_post)
            db.commit()

            # Creative Brief
            creative_out = self.creative_agent.execute(db, campaign_id, {"post": draft.model_dump()})
            db_creative = CreativeBriefModel(
                post_id=post_id,
                visual_concept=creative_out.visual_concept,
                asset_type=creative_out.asset_type,
                visual_hook=creative_out.visual_hook,
                scene_description=creative_out.scene_description,
                on_screen_text=creative_out.on_screen_text,
                brand_direction=creative_out.brand_direction
            )
            db.add(db_creative)
            db.commit()

            # Compliance Review Loop (Max 3 retries)
            self._run_compliance_loop(db, campaign, db_post, db_creative)

        # Transition to HUMAN_REVIEW gate
        campaign.status = "HUMAN_REVIEW"
        db.commit()

        self.log_and_send(
            db=db,
            campaign_id=campaign_id,
            recipient="HumanOperator",
            message_type="CAMPAIGN_READY_FOR_HUMAN_REVIEW",
            payload={"campaign_id": campaign_id, "posts_count": len(campaign.posts)},
            action="Submitted Campaign for Human Approval Gate",
            input_summary="Completed Agent & Compliance Review",
            output_summary=f"Campaign transitioning to HUMAN_REVIEW state."
        )

        return {"status": "HUMAN_REVIEW", "campaign_id": campaign_id}

    def _run_compliance_loop(self, db: Session, campaign: CampaignModel, post: PostModel, creative: CreativeBriefModel):
        """
        Enforces maximum 3 compliance revision attempts.
        """
        max_attempts = 3
        rejection_feedback = None

        for attempt in range(1, max_attempts + 1):
            post.compliance_attempts = attempt
            db.commit()

            # Execute Compliance Review
            comp_eval = self.compliance_agent.execute(db, campaign.id, {
                "post": {
                    "channel": post.channel,
                    "format": post.format,
                    "hook": post.hook,
                    "copy": post.copy,
                    "cta": post.cta,
                    "hashtags": post.hashtags
                },
                "creative_brief": {
                    "visual_concept": creative.visual_concept,
                    "on_screen_text": creative.on_screen_text
                },
                "campaign_brief": campaign.human_brief,
                "revision_count": attempt
            })

            # Record Review in DB
            db_review = ComplianceReviewModel(
                post_id=post.id,
                attempt_number=attempt,
                approved=comp_eval.approved,
                score=comp_eval.score,
                issues=comp_eval.issues,
                required_changes=comp_eval.required_changes,
                reasoning=comp_eval.reasoning
            )
            db.add(db_review)
            db.commit()

            if comp_eval.approved:
                post.compliance_status = "APPROVED"
                db.commit()
                return

            # Rejection Handling
            rejection_feedback = {
                "previous_copy": post.copy,
                "issues": comp_eval.issues,
                "required_changes": comp_eval.required_changes,
                "reasoning": comp_eval.reasoning
            }

            if attempt < max_attempts:
                # Ask Content Agent to revise
                revised_content = self.content_agent.execute(db, campaign.id, {
                    "strategy": {
                        "objective": campaign.human_brief,
                        "content_pillars": campaign.content_pillars,
                        "channels": [post.channel]
                    },
                    "rejection_feedback": rejection_feedback,
                    "revision_count": attempt + 1
                })
                
                if revised_content.posts:
                    rev_post = revised_content.posts[0]
                    post.copy = rev_post.copy
                    post.hook = rev_post.hook
                    post.cta = rev_post.cta
                    post.hashtags = rev_post.hashtags
                    db.commit()

        # Failed 3 times - Escalate to Human
        post.compliance_status = "ESCALATED_HUMAN"
        db.commit()
        
        self.log_and_send(
            db=db,
            campaign_id=campaign.id,
            recipient="HumanOperator",
            message_type="COMPLIANCE_ESCALATION",
            payload={"post_id": post.id, "reason": "Failed 3 compliance revision attempts."},
            action=f"Escalated Post {post.id} to Human Review after 3 compliance rejections",
            input_summary="Exceeded max 3 revision attempts",
            output_summary="Marked compliance_status as ESCALATED_HUMAN",
            status="ESCALATED",
            revision_count=max_attempts
        )

    def publish_and_simulate_week(self, db: Session, campaign_id: str, week_number: int = 1) -> Dict[str, Any]:
        """
        Publishes approved posts to Mock Platform, simulates engagement + comments, and runs Community Manager.
        """
        campaign = db.query(CampaignModel).filter(CampaignModel.id == campaign_id).first()
        if not campaign:
            raise ValueError("Campaign not found")

        # Get approved posts for this week
        approved_posts = db.query(PostModel).filter(
            PostModel.campaign_id == campaign_id,
            PostModel.week_number == week_number,
            PostModel.human_approval_status == "APPROVED"
        ).all()

        if not approved_posts:
            raise ValueError(f"No human-approved posts found for Week {week_number}. Human approval required.")

        campaign.status = "SCHEDULED"
        db.commit()

        # 1. Schedule posts via SchedulerAgent
        calendar_res = self.scheduler_agent.execute(db, campaign_id, {
            "approved_posts": [{"id": p.id, "channel": p.channel, "format": p.format, "hook": p.hook, "copy": p.copy, "cta": p.cta, "hashtags": p.hashtags} for p in approved_posts],
            "week_number": week_number
        })

        campaign.status = "PUBLISHED"
        db.commit()

        # 2. Publish posts to Mock Social Platform and generate simulated engagement + comments
        published_platform_posts = []
        for post in approved_posts:
            platform_post = MockPlatformService.publish_approved_post(db, post)
            published_platform_posts.append(platform_post)

        # 3. Community Manager processes audience comments
        all_comments_payload = []
        for p_post in published_platform_posts:
            comments = MockPlatformService.get_post_comments(db, p_post.id)
            for c in comments:
                all_comments_payload.append({"id": c.id, "author": c.author, "content": c.content})

        if all_comments_payload:
            self.community_agent.execute(db, campaign_id, {"comments": all_comments_payload})

        # 4. Run Analytics Agent for Week
        campaign.status = "ANALYZING"
        db.commit()

        post_metrics = [
            {
                "id": p.id,
                "channel": p.channel,
                "format": p.format,
                "scheduled_time": p.scheduled_time,
                "hook": p.hook,
                "post_copy": p.post_copy,
                "hashtags": p.hashtags,
                "impressions": p.impressions,
                "likes": p.likes,
                "comments_count": p.comments_count,
                "shares": p.shares,
                "saves": p.saves,
                "clicks": p.clicks,
                "engagement_rate": p.engagement_rate
            } for p in published_platform_posts
        ]

        analytics_out = self.analytics_agent.execute(db, campaign_id, {
            "week_number": week_number,
            "kpis": campaign.kpis,
            "post_metrics": post_metrics,
            "comments_summary": f"Analyzed {len(all_comments_payload)} audience comments across Pulse, Forum, ProNet."
        })

        if week_number == 1:
            campaign.week1_analytics_report = analytics_out.model_dump()
            recs = [r.model_dump() for r in (analytics_out.recommendations or [])]
            if not recs:
                recs = [{
                    "category": "Copy Length",
                    "channel": "Pulse",
                    "observation": "Single post performance benchmarked across channels",
                    "evidence": "n=1 post per channel",
                    "hypothesis": "Refining opening hook and post length will improve initial engagement rate",
                    "confidence": "Low (n=1 sample)",
                    "recommendation": "Maintain post cadence and test concise opening hooks on Pulse"
                }]
            campaign.week2_recommendations = recs
            campaign.status = "IMPROVEMENT"
            db.commit()

        return {
            "published_count": len(published_platform_posts),
            "analytics_report": analytics_out.model_dump()
        }

    def run_campaign_week2(self, db: Session, campaign_id: str) -> Dict[str, Any]:
        """
        Executes Week 2 Closed Feedback Loop:
        Consumes Week 1 Analytics recommendations -> Strategy Agent -> Week 2 Posts -> Compliance -> Human Approval -> Publish -> Analytics Comparison!
        """
        campaign = db.query(CampaignModel).filter(CampaignModel.id == campaign_id).first()
        if not campaign:
            raise ValueError("Campaign not found")

        if not campaign.week2_recommendations:
            raise ValueError("Week 1 Analytics report missing. Run Week 1 first.")

        campaign.week_number = 2
        campaign.status = "AGENT_REVIEW"
        db.commit()

        self.log_and_send(
            db=db,
            campaign_id=campaign_id,
            recipient="StrategyAgent",
            message_type="WEEK2_FEEDBACK_LOOP_START",
            payload={"recommendations": campaign.week2_recommendations},
            action="Initiated Week 2 Feedback Loop passing Analytics Recommendations to Strategy",
            input_summary=f"Passing {len(campaign.week2_recommendations)} evidence-backed recommendations",
            output_summary="Feeding Analytics insight back into Strategy Agent"
        )

        # 1. Revised Strategy Agent with Analytics Feedback
        strategy_out = self.strategy_agent.execute(db, campaign_id, {
            "human_brief": campaign.human_brief,
            "week_number": 2,
            "analytics_recommendations": campaign.week2_recommendations
        })

        campaign.week2_strategy_adjustments = strategy_out.model_dump()
        campaign.status = "COMPLIANCE"
        db.commit()

        # 2. Content Agent creates Week 2 Posts
        content_out = self.content_agent.execute(db, campaign_id, {
            "strategy": strategy_out.model_dump(),
            "week_number": 2
        })

        # Process each Week 2 post through Creative & Compliance Loop
        for draft in content_out.posts:
            post_id = f"post_w2_{uuid.uuid4().hex[:8]}"
            db_post = PostModel(
                id=post_id,
                campaign_id=campaign_id,
                week_number=2,
                channel=draft.channel,
                scheduled_time=draft.scheduled_time,
                format=draft.format,
                copy=draft.copy,
                hook=draft.hook,
                cta=draft.cta,
                hashtags=draft.hashtags,
                content_pillar=draft.content_pillar,
                compliance_status="PENDING",
                compliance_attempts=0,
                human_approval_status="PENDING"
            )
            db.add(db_post)
            db.commit()

            creative_out = self.creative_agent.execute(db, campaign_id, {"post": draft.model_dump()})
            db_creative = CreativeBriefModel(
                post_id=post_id,
                visual_concept=creative_out.visual_concept,
                asset_type=creative_out.asset_type,
                visual_hook=creative_out.visual_hook,
                scene_description=creative_out.scene_description,
                on_screen_text=creative_out.on_screen_text,
                brand_direction=creative_out.brand_direction
            )
            db.add(db_creative)
            db.commit()

            self._run_compliance_loop(db, campaign, db_post, db_creative)

        campaign.status = "HUMAN_REVIEW"
        db.commit()

        return {"status": "HUMAN_REVIEW", "campaign_id": campaign_id, "week_number": 2}
