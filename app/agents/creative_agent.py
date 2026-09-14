from typing import Dict, Any
from sqlalchemy.orm import Session
from app.agents.base_agent import BaseAgent
from app.llm.schemas import CreativeBriefOutput

CREATIVE_SYSTEM_PROMPT = """You are the Creative & Art Director Agent for a social media AI agency.
Your task is to design detailed visual and creative briefs for social media posts.
For each post provided, generate a creative brief specifying:
1. Visual Concept & Art Direction
2. Asset Type (short_video, static_image, carousel, text_graphic)
3. Visual Hook (first 2-second visual element or graphic layout)
4. Scene Description (frame-by-frame or layout composition)
5. On-Screen Text / Typography
6. Brand Styling & Color Direction

Ensure visual suggestions match the target channel:
- Pulse: Dynamic video transition, high energy, vibrant color.
- Forum: Clean graphic, infographics, relatable authentic visual.
- ProNet: Professional diagram, sleek infographic, modern typography.
"""

class CreativeAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="CreativeAgent",
            role="Creative & Art Director",
            system_prompt=CREATIVE_SYSTEM_PROMPT
        )

    def execute(self, db: Session, campaign_id: str, payload: Dict[str, Any]) -> CreativeBriefOutput:
        post = payload.get("post", {})
        channel = post.get("channel", "Pulse")
        copy = post.get("copy", "")
        hook = post.get("hook", "")
        format_type = post.get("format", "video_script")

        user_prompt = (
            f"POST DETAILS:\n"
            f"Channel: {channel}\n"
            f"Format: {format_type}\n"
            f"Hook: {hook}\n"
            f"Copy: {copy}\n\n"
            f"Create a structured creative brief for this post."
        )

        creative_output = self.generate_structured(user_prompt, CreativeBriefOutput, temperature=0.4)

        self.log_and_send(
            db=db,
            campaign_id=campaign_id,
            recipient="ComplianceAgent",
            message_type="CREATIVE_BRIEF_GENERATED",
            payload=creative_output.model_dump(),
            action=f"Generated Creative Brief for {channel} post",
            input_summary=f"Post Channel: {channel}, Hook: {hook[:50]}...",
            output_summary=f"Asset Type: {creative_output.asset_type}, Concept: {creative_output.visual_concept[:60]}..."
        )

        return creative_output
