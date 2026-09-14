from typing import List, Optional, Dict, Any, Union
from pydantic import BaseModel, Field

# --- STRATEGY AGENT SCHEMAS ---
class TargetAudienceSchema(BaseModel):
    demographic: str = Field(description="Age range, target group, status")
    pain_points: List[str] = Field(description="Key customer frustrations or desires")
    preferred_channels: List[str] = Field(description="Channels where audience is most active")

class StrategyOutput(BaseModel):
    objective: str = Field(description="Overall campaign objective")
    target_audience: TargetAudienceSchema
    channels: List[str] = Field(description="Selected distribution channels")
    duration_days: int = Field(default=14, description="Campaign duration in days")
    content_pillars: List[str] = Field(description="Core content themes/pillars")
    posting_cadence: Union[Dict[str, Any], List[Any], str] = Field(description="Channel to posting frequency map (e.g. {'Pulse': 'Daily'})")
    kpis: List[str] = Field(description="Key metrics to measure campaign success")
    strategic_hypotheses: List[str] = Field(description="Initial hypotheses regarding copy, hooks, timing")


# --- CONTENT AGENT SCHEMAS ---
class PostDraft(BaseModel):
    channel: str = Field(description="Target channel: Pulse, Forum, or ProNet")
    format: str = Field(description="Content format: video_script, text_post, infographic_carousel, Q_and_A")
    scheduled_time: str = Field(default="18:00", description="Suggested time e.g. 18:30")
    hook: str = Field(default="", description="Attention-grabbing opening line")
    copy: str = Field(description="Main post text body")
    cta: str = Field(default="Learn more in the link below!", description="Call to action text")
    hashtags: List[str] = Field(default_factory=list, description="List of 1 to 4 relevant hashtags")
    content_pillar: str = Field(default="General", description="Associated content pillar")

class ContentOutput(BaseModel):
    posts: List[PostDraft] = Field(description="Generated posts for campaign")


# --- CREATIVE AGENT SCHEMAS ---
class CreativeBriefOutput(BaseModel):
    visual_concept: str = Field(description="Overall visual direction")
    asset_type: str = Field(description="Visual asset type: short_video, static_image, carousel, text_graphic")
    visual_hook: str = Field(description="Initial visual graphic element or thumbnail concept")
    scene_description: Optional[str] = Field(default="", description="Step-by-step description of visual composition or video scene")
    on_screen_text: Optional[str] = Field(default="", description="Text displayed on screen/graphic")
    brand_direction: Optional[str] = Field(default="", description="Color, typography, and mood notes")


# --- COMPLIANCE AGENT SCHEMAS ---
class ComplianceOutput(BaseModel):
    approved: bool = Field(description="True if post complies with brand and legal guidelines, False otherwise")
    score: float = Field(description="Quality and safety score from 0 to 100")
    issues: List[str] = Field(default=[], description="List of detected compliance issues")
    required_changes: List[str] = Field(default=[], description="Specific revision instructions if rejected")
    reasoning: str = Field(description="Detailed explanation of compliance evaluation")


# --- COMMUNITY MANAGER AGENT SCHEMAS ---
class CommunityResponseOutput(BaseModel):
    sentiment: str = Field(description="Classification: positive, neutral, negative, question, complaint, sensitive")
    is_sensitive: bool = Field(description="True if comment requires human escalation")
    response_draft: Optional[str] = Field(default=None, description="Draft response to public comment")
    reasoning: str = Field(description="Explanation of classification and reply strategy")


from pydantic import BaseModel, Field, model_validator

# --- ANALYTICS AGENT SCHEMAS ---
class AnalyticsRecommendation(BaseModel):
    channel: str = Field(description="Target channel name (Pulse, Forum, ProNet, or All Channels)")
    category: str = Field(description="timing, copy_length, tone, format, hashtag, cta")
    observation: str = Field(description="Direct metric observation comparing posts within the SAME channel or metric dimension")
    evidence: str = Field(description="Sample size and exact metric data (e.g. n=1 post per channel, ER: 14.2% vs 10.1%)")
    hypothesis: str = Field(description="Plausible explanation for observed metric difference")
    confidence: str = Field(description="Confidence level: High, Medium, Low, or Insufficient Evidence")
    recommendation: Optional[str] = Field(default=None, description="Actionable instruction or 'Insufficient evidence to change'")
    instruction: Optional[str] = Field(default=None, description="Alias for recommendation instruction")

    @model_validator(mode='after')
    def sync_recommendation_fields(self):
        if not self.recommendation and self.instruction:
            self.recommendation = self.instruction
        elif not self.instruction and self.recommendation:
            self.instruction = self.recommendation
        if not self.recommendation:
            self.recommendation = "Insufficient evidence to change"
        return self

class AnalyticsOutput(BaseModel):
    kpi_evaluation: Union[Dict[str, Any], List[Any], str] = Field(default="", description="Assessment of start KPIs vs achieved metrics")
    top_posts_analysis: Optional[List[Any]] = Field(default=[], description="Insights on top performing posts and why")
    bottom_posts_analysis: Optional[List[Any]] = Field(default=[], description="Insights on lower performing posts and why")
    discovered_patterns: Union[Dict[str, Any], List[Any], str] = Field(default="", description="Key patterns across timing, copy length, tone, formats")
    comment_sentiment_summary: Optional[Union[Dict[str, Any], List[Any], str]] = Field(default="", description="Audience reception and recurring themes")
    recommendations: Optional[List[AnalyticsRecommendation]] = Field(default=[], description="Actionable recommendations for Week 2")
