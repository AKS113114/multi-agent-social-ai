from typing import Dict, Any, List
from sqlalchemy.orm import Session
from app.agents.base_agent import BaseAgent
from app.llm.schemas import ContentOutput, PostDraft
from app.config import settings

CONTENT_SYSTEM_PROMPT = """You are the Senior Content Writer Agent for a social media agency.
Your task is to write platform-specific posts tailored strictly to each channel's character:
- Pulse: Short-form video script/caption. Punchy opening hook, high energy, under 60 words.
- Forum: Community discussion post. Start with an intriguing question/hook, foster open discussion, conversational, 50-120 words.
- ProNet: Professional insight post. Value-driven, structured bullet points or ROI focus, professional tone, 80-160 words.

IMPORTANT CHANNEL CONSTRAINTS:
1. Pulse copy must be brief (<60 words) and energetic.
2. Forum copy must end with an engaging question CTA.
3. ProNet copy must remain polished and professional without casual slang.
4. Include 1 to 3 relevant hashtags per post.

If revising a post due to Compliance Rejection, carefully fix all required changes specified in the feedback.
"""

class ContentAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="ContentAgent",
            role="Senior Social Media Copywriter",
            system_prompt=CONTENT_SYSTEM_PROMPT
        )

    def execute(self, db: Session, campaign_id: str, payload: Dict[str, Any]) -> ContentOutput:
        strategy = payload.get("strategy", {})
        rejection_feedback = payload.get("rejection_feedback", None)
        week_number = payload.get("week_number", 1)

        user_prompt = (
            f"CAMPAIGN STRATEGY (WEEK {week_number}):\n"
            f"Objective: {strategy.get('objective')}\n"
            f"Target Audience: {strategy.get('target_audience')}\n"
            f"Pillars: {strategy.get('content_pillars')}\n"
            f"Channels: {strategy.get('channels')}\n"
        )

        if rejection_feedback:
            user_prompt += (
                f"\n\nTHIS IS A REVISION ATTEMPT (Attempt #{payload.get('revision_count', 1)}):\n"
                f"Previous Post Copy: {rejection_feedback.get('previous_copy')}\n"
                f"Compliance Issues: {rejection_feedback.get('issues')}\n"
                f"Required Changes: {rejection_feedback.get('required_changes')}\n"
                f"Reasoning: {rejection_feedback.get('reasoning')}\n"
                f"Please fix all these issues specifically in your revised posts."
            )
        else:
            user_prompt += "\nCreate a set of posts covering Pulse, Forum, and ProNet for this campaign week."

        user_prompt += f"\n\nCHANNEL SPECIFICATIONS:\n{settings.CHANNELS}"

        content_output = self.generate_structured(user_prompt, ContentOutput, temperature=0.5)

        action_name = f"Revised Content (Attempt #{payload.get('revision_count', 1)})" if rejection_feedback else f"Generated Content for Week {week_number}"
        
        self.log_and_send(
            db=db,
            campaign_id=campaign_id,
            recipient="CreativeAgent",
            message_type="CONTENT_GENERATED",
            payload=content_output.model_dump(),
            action=action_name,
            input_summary=f"Strategy pillars: {strategy.get('content_pillars')}",
            output_summary=f"Generated {len(content_output.posts)} posts across channels",
            revision_count=payload.get('revision_count', 0)
        )

        return content_output
