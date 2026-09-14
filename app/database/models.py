from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, Boolean, Float, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from app.database.database import Base

class CampaignModel(Base):
    __tablename__ = "campaigns"

    id = Column(String, primary_key=True, index=True) # campaign_id
    title = Column(String, nullable=False)
    human_brief = Column(Text, nullable=False)
    target_audience = Column(JSON, nullable=True) # structured audience profile
    channels = Column(JSON, nullable=True) # list of channels
    duration_days = Column(Integer, default=14)
    content_pillars = Column(JSON, nullable=True)
    posting_cadence = Column(JSON, nullable=True)
    kpis = Column(JSON, nullable=True)
    strategic_hypotheses = Column(JSON, nullable=True)
    status = Column(String, default="DRAFT") # DRAFT, AGENT_REVIEW, COMPLIANCE, HUMAN_REVIEW, APPROVED, SCHEDULED, PUBLISHED, ANALYZING, IMPROVEMENT
    week_number = Column(Integer, default=1) # 1 or 2
    
    # Week 2 Specifics
    week1_analytics_report = Column(JSON, nullable=True)
    week2_recommendations = Column(JSON, nullable=True)
    week2_strategy_adjustments = Column(JSON, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    posts = relationship("PostModel", back_populates="campaign", cascade="all, delete-orphan")
    messages = relationship("AgentMessageModel", back_populates="campaign", cascade="all, delete-orphan")
    traces = relationship("AgentTraceModel", back_populates="campaign", cascade="all, delete-orphan")


class PostModel(Base):
    __tablename__ = "posts"

    id = Column(String, primary_key=True, index=True) # post_id
    campaign_id = Column(String, ForeignKey("campaigns.id"), nullable=False)
    week_number = Column(Integer, default=1)
    channel = Column(String, nullable=False) # Pulse, Forum, ProNet
    scheduled_time = Column(String, nullable=True) # e.g. "18:30" or ISO string
    format = Column(String, nullable=False) # video_script, text_post, infographic_carousel, Q_and_A
    copy = Column(Text, nullable=False)
    hook = Column(Text, nullable=True)
    cta = Column(Text, nullable=True)
    hashtags = Column(JSON, nullable=True) # list of hashtags
    content_pillar = Column(String, nullable=True)
    
    compliance_status = Column(String, default="PENDING") # PENDING, APPROVED, REJECTED, ESCALATED_HUMAN
    compliance_attempts = Column(Integer, default=0)
    human_approval_status = Column(String, default="PENDING") # PENDING, APPROVED, REJECTED, REVISION_REQUESTED
    human_feedback = Column(Text, nullable=True)
    
    is_published = Column(Boolean, default=False)
    platform_post_id = Column(String, nullable=True) # linked mock platform post ID

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    campaign = relationship("CampaignModel", back_populates="posts")
    creative_brief = relationship("CreativeBriefModel", back_populates="post", uselist=False, cascade="all, delete-orphan")
    compliance_reviews = relationship("ComplianceReviewModel", back_populates="post", cascade="all, delete-orphan")


class CreativeBriefModel(Base):
    __tablename__ = "creative_briefs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    post_id = Column(String, ForeignKey("posts.id"), nullable=False, unique=True)
    visual_concept = Column(Text, nullable=False)
    asset_type = Column(String, nullable=False) # short_video, static_image, carousel, text_graphic
    visual_hook = Column(Text, nullable=True)
    scene_description = Column(Text, nullable=True)
    on_screen_text = Column(Text, nullable=True)
    brand_direction = Column(Text, nullable=True)

    post = relationship("PostModel", back_populates="creative_brief")


class ComplianceReviewModel(Base):
    __tablename__ = "compliance_reviews"

    id = Column(Integer, primary_key=True, autoincrement=True)
    post_id = Column(String, ForeignKey("posts.id"), nullable=False)
    attempt_number = Column(Integer, nullable=False)
    approved = Column(Boolean, nullable=False)
    score = Column(Float, nullable=False) # 0 to 100
    issues = Column(JSON, nullable=True) # list of issues
    required_changes = Column(JSON, nullable=True) # list of changes
    reasoning = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    post = relationship("PostModel", back_populates="compliance_reviews")


class PlatformPostModel(Base):
    __tablename__ = "platform_posts"

    id = Column(String, primary_key=True, index=True)
    campaign_id = Column(String, nullable=False)
    week_number = Column(Integer, default=1)
    channel = Column(String, nullable=False)
    post_copy = Column(Text, nullable=False)
    hook = Column(Text, nullable=True)
    cta = Column(Text, nullable=True)
    hashtags = Column(JSON, nullable=True)
    format = Column(String, nullable=False)
    published_at = Column(DateTime, default=datetime.utcnow)
    scheduled_time = Column(String, nullable=True)
    
    # Simulated metrics
    impressions = Column(Integer, default=0)
    likes = Column(Integer, default=0)
    comments_count = Column(Integer, default=0)
    shares = Column(Integer, default=0)
    saves = Column(Integer, default=0)
    clicks = Column(Integer, default=0)
    follower_delta = Column(Integer, default=0)
    engagement_rate = Column(Float, default=0.0)

    comments = relationship("PlatformCommentModel", back_populates="platform_post", cascade="all, delete-orphan")


class PlatformCommentModel(Base):
    __tablename__ = "platform_comments"

    id = Column(String, primary_key=True, index=True)
    platform_post_id = Column(String, ForeignKey("platform_posts.id"), nullable=False)
    author = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    sentiment = Column(String, nullable=False) # positive, neutral, negative, question, complaint, sensitive
    is_sensitive = Column(Boolean, default=False)
    community_response = Column(Text, nullable=True)
    response_status = Column(String, default="PENDING") # PENDING, RESPONDED, ESCALATED
    created_at = Column(DateTime, default=datetime.utcnow)

    platform_post = relationship("PlatformPostModel", back_populates="comments")


class AgentMessageModel(Base):
    __tablename__ = "agent_messages"

    id = Column(String, primary_key=True, index=True) # message_id
    campaign_id = Column(String, ForeignKey("campaigns.id"), nullable=False)
    sender = Column(String, nullable=False)
    recipient = Column(String, nullable=False)
    message_type = Column(String, nullable=False)
    payload = Column(JSON, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
    parent_message_id = Column(String, nullable=True)
    status = Column(String, default="SENT") # SENT, DELIVERED, PROCESSED, FAILED

    campaign = relationship("CampaignModel", back_populates="messages")


class AgentTraceModel(Base):
    __tablename__ = "agent_traces"

    id = Column(Integer, primary_key=True, autoincrement=True)
    campaign_id = Column(String, ForeignKey("campaigns.id"), nullable=False)
    agent = Column(String, nullable=False)
    action = Column(String, nullable=False)
    input_summary = Column(Text, nullable=True)
    output_summary = Column(Text, nullable=True)
    status = Column(String, default="SUCCESS") # SUCCESS, REJECTED, ESCALATED, RETRIED, ERROR
    revision_count = Column(Integer, default=0)
    handoff_to = Column(String, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)

    campaign = relationship("CampaignModel", back_populates="traces")


class CampaignMemoryModel(Base):
    __tablename__ = "campaign_memory"

    id = Column(Integer, primary_key=True, autoincrement=True)
    campaign_id = Column(String, nullable=False)
    key = Column(String, nullable=False, index=True) # e.g. "top_performing_hook", "channel_timing_insight"
    content = Column(JSON, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
