import uuid
from datetime import datetime
from sqlalchemy.orm import Session
from app.database.database import SessionLocal, init_db
from app.database.models import (
    CampaignModel, PostModel, CreativeBriefModel, ComplianceReviewModel,
    PlatformPostModel, PlatformCommentModel, AgentTraceModel, AgentMessageModel
)

DEMO_BRIEF = (
    "We are launching a budget espresso machine for students. "
    "Run a two-week awareness campaign across our three channels, "
    "target price-sensitive 18–25 year olds, keep the tone playful, don't over-promise."
)

def seed_database():
    init_db()
    db: Session = SessionLocal()

    existing = db.query(CampaignModel).filter(CampaignModel.title == "Student Espresso Machine Launch").first()
    if existing:
        print("[SEED] Demo campaign already exists. Skipping seed.")
        db.close()
        return existing.id

    print("[SEED] Seeding demo campaign data...")
    cmp_id = f"cmp_demo_espresso"
    
    # 1. Create Campaign
    campaign = CampaignModel(
        id=cmp_id,
        title="Student Espresso Machine Launch",
        human_brief=DEMO_BRIEF,
        status="IMPROVEMENT",
        week_number=1,
        target_audience={
            "demographic": "18-25 year old college students and budget-conscious young adults",
            "pain_points": ["Expensive coffee shop habits", "Tiny dorm space", "Complex coffee machines"],
            "preferred_channels": ["Pulse", "Forum", "ProNet"]
        },
        channels=["Pulse", "Forum", "ProNet"],
        duration_days=14,
        content_pillars=["Affordable Quality", "Dorm Room Espresso", "Morning Routine Hacks"],
        posting_cadence={"Pulse": "Daily", "Forum": "3x/week", "ProNet": "2x/week"},
        kpis=["Cost-per-click under $0.50", "Engagement Rate > 4.5%", "High comment inquiry rate"],
        strategic_hypotheses=[
            "Short energetic video clips on Pulse will drive highest reach among 18-22 year olds.",
            "Ending Forum discussion posts with questions will increase audience participation."
        ],
        week1_analytics_report={
            "kpi_evaluation": {"Engagement Rate": "Achieved 4.85% (Target 4.5%)", "Reach": "Pulse peak window generated 38% higher impressions"},
            "top_posts_analysis": ["Pulse post #1 at 18:30 hit peak window and short copy (<60 words) resulted in 5,420 impressions."],
            "bottom_posts_analysis": ["ProNet post published at 09:00 with casual slang ('bruh') suffered a 35% reach penalty."],
            "discovered_patterns": {
                "timing": "Pulse performs best 17:00-21:00. Forum performs best 12:00-15:00 and 18:00-21:00.",
                "length": "Pulse copy > 60 words was penalized. Forum posts 40-120 words excelled.",
                "cta": "Posts with question CTAs received 1.6x more comments."
            },
            "comment_sentiment_summary": "78% positive/curious, 15% pricing questions, 7% feature inquiries.",
            "recommendations": [
                {
                    "channel": "Pulse",
                    "category": "timing",
                    "recommendation": "Shift all Pulse posts to 18:30 peak window.",
                    "evidence": "18:30 posts generated 1.35x median impressions compared to morning slots."
                },
                {
                    "channel": "Forum",
                    "category": "cta",
                    "recommendation": "Ensure every Forum post ends with a direct question CTA.",
                    "evidence": "Question CTAs boosted comment count by +65%."
                },
                {
                    "channel": "ProNet",
                    "category": "tone",
                    "recommendation": "Eliminate informal slang; use structured value bullet points.",
                    "evidence": "Slang-heavy post received 35% lower reach penalty on ProNet."
                }
            ]
        },
        week2_recommendations=[
            {
                "channel": "Pulse",
                "category": "timing",
                "recommendation": "Shift all Pulse posts to 18:30 peak window.",
                "evidence": "18:30 posts generated 1.35x median impressions compared to morning slots."
            },
            {
                "channel": "Forum",
                "category": "cta",
                "recommendation": "Ensure every Forum post ends with a direct question CTA.",
                "evidence": "Question CTAs boosted comment count by +65%."
            },
            {
                "channel": "ProNet",
                "category": "tone",
                "recommendation": "Eliminate informal slang; use structured value bullet points.",
                "evidence": "Slang-heavy post received 35% lower reach penalty on ProNet."
            }
        ]
    )
    db.add(campaign)

    # 2. Add Week 1 Posts & Reviews
    posts_data = [
        {
            "id": "post_w1_pulse",
            "channel": "Pulse",
            "format": "video_script",
            "scheduled_time": "18:30",
            "hook": "Dorm room coffee hack for under $100! ☕⚡",
            "copy": "Tired of spending $7 on iced lattes before your 9 AM lecture? Meet the compact budget espresso machine designed for student desks.",
            "cta": "Tap the link to grab student discount code!",
            "hashtags": ["#StudentCoffee", "#DormLife", "#EspressoHack"],
            "pillar": "Affordable Quality",
            "imp": 5420, "likes": 325, "cmts": 68, "shares": 135, "saves": 82, "clicks": 95, "er": 5.4
        },
        {
            "id": "post_w1_forum",
            "channel": "Forum",
            "format": "Q_and_A",
            "scheduled_time": "13:00",
            "hook": "Is a $99 espresso machine actually capable of real 9-bar extraction?",
            "copy": "Most budget espresso makers use pressurized baskets that fake cremac, but we built this compact unit with a real 15-bar Italian pump. What's your biggest coffee frustration in college?",
            "cta": "Drop your thoughts below!",
            "hashtags": ["#CoffeeGeeks", "#StudentTech"],
            "pillar": "Dorm Room Espresso",
            "imp": 3850, "likes": 178, "cmts": 124, "shares": 42, "saves": 38, "clicks": 72, "er": 5.1
        },
        {
            "id": "post_w1_pronet",
            "channel": "ProNet",
            "format": "text_post",
            "scheduled_time": "09:00",
            "hook": "Why affordable hardware design matters for the next generation of consumers.",
            "copy": "Bruh, students shouldn't have to break the bank for decent espresso. We engineered this unit to deliver high ROI for price-sensitive grads.",
            "cta": "Read our engineering design case study.",
            "hashtags": ["#ProductDesign", "#HardwareStartup"],
            "pillar": "Morning Routine Hacks",
            "imp": 1820, "likes": 58, "cmts": 18, "shares": 12, "saves": 10, "clicks": 28, "er": 3.4
        }
    ]

    for p in posts_data:
        post = PostModel(
            id=p["id"],
            campaign_id=cmp_id,
            week_number=1,
            channel=p["channel"],
            scheduled_time=p["scheduled_time"],
            format=p["format"],
            copy=p["copy"],
            hook=p["hook"],
            cta=p["cta"],
            hashtags=p["hashtags"],
            content_pillar=p["pillar"],
            compliance_status="APPROVED",
            human_approval_status="APPROVED",
            is_published=True,
            platform_post_id=f"plat_{p['id']}"
        )
        db.add(post)

        creative = CreativeBriefModel(
            post_id=p["id"],
            visual_concept=f"Dynamic visual concept for {p['channel']}",
            asset_type="short_video" if p["channel"] == "Pulse" else "static_image",
            visual_hook="Close-up espresso shot pouring into glass cup",
            scene_description="Fast-paced dorm aesthetic with student making latte",
            on_screen_text="Student Espresso Machine — Under $100",
            brand_direction="Vibrant, clean, warm coffee tones"
        )
        db.add(creative)

        review = ComplianceReviewModel(
            post_id=p["id"],
            attempt_number=1,
            approved=True,
            score=92.0,
            issues=[],
            required_changes=[],
            reasoning="Verified no false claims or over-promising. Tone is compliant."
        )
        db.add(review)

        plat_post = PlatformPostModel(
            id=f"plat_{p['id']}",
            campaign_id=cmp_id,
            week_number=1,
            channel=p["channel"],
            post_copy=p["copy"],
            hook=p["hook"],
            cta=p["cta"],
            hashtags=p["hashtags"],
            format=p["format"],
            scheduled_time=p["scheduled_time"],
            published_at=datetime.utcnow(),
            impressions=p["imp"],
            likes=p["likes"],
            comments_count=p["cmts"],
            shares=p["shares"],
            saves=p["saves"],
            clicks=p["clicks"],
            follower_delta=int(p["likes"] * 0.1),
            engagement_rate=p["er"]
        )
        db.add(plat_post)

        # Comments for Platform Post
        comment = PlatformCommentModel(
            id=f"cmt_{p['id']}_1",
            platform_post_id=f"plat_{p['id']}",
            author="dorm_barista22",
            content="Wait this looks awesome! Does it come with a student warranty?",
            sentiment="question",
            is_sensitive=False,
            community_response="Hi dorm_barista22! Yes, it includes a 1-year full student replacement warranty!",
            response_status="RESPONDED"
        )
        db.add(comment)

    # 3. Add Agent Traces
    traces_data = [
        ("OrchestratorAgent", "Parsed human brief and instructed Strategy Agent", "Brief: We are launching a budget espresso machine...", "Decomposed requirements for Week 1", "SUCCESS"),
        ("StrategyAgent", "Generated Strategy for Week 1", "Human Brief", "Pillars: Affordable Quality, Dorm Room Espresso | Channels: Pulse, Forum, ProNet", "SUCCESS"),
        ("ContentAgent", "Generated Content for Week 1", "Strategy Pillars", "Generated 3 posts across channels", "SUCCESS"),
        ("ComplianceAgent", "Compliance Audit APPROVED (Score: 92.0/100)", "Post for Pulse, Revision Attempt #1", "Status: APPROVED, Issues: 0", "APPROVED"),
        ("OrchestratorAgent", "Submitted Campaign for Human Approval Gate", "Completed Agent & Compliance Review", "Campaign transitioning to HUMAN_REVIEW state.", "SUCCESS"),
        ("SchedulerAgent", "Scheduled 3 posts for Week 1", "Approved Posts: 3", "Created publishing calendar across Pulse, Forum, ProNet", "SUCCESS"),
        ("CommunityManagerAgent", "Processed 3 incoming audience comments", "Evaluated comments from mock platform", "Responded: 3, Escalated: 0", "SUCCESS"),
        ("AnalyticsAgent", "Completed Weekly Analytics Report for Week 1", "Analyzed 3 posts for Week 1", "Generated 3 concrete recommendations for Week 2", "SUCCESS")
    ]

    for agent, action, inp, outp, st in traces_data:
        t = AgentTraceModel(
            campaign_id=cmp_id,
            agent=agent,
            action=action,
            input_summary=inp,
            output_summary=outp,
            status=st,
            timestamp=datetime.utcnow()
        )
        db.add(t)

    db.commit()
    db.close()
    print(f"[SEED] Successfully seeded demo campaign '{cmp_id}'!")
    return cmp_id
