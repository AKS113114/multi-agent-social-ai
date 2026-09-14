from typing import Dict, Any, Optional
from sqlalchemy.orm import Session
from app.agents.base_agent import BaseAgent
from app.llm.schemas import StrategyOutput
from app.config import settings

STRATEGY_SYSTEM_PROMPT = """You are the Lead Strategy Agent for a high-performing Social Media AI Agency.
Your job is to analyze campaign briefs and formulate data-backed social media strategies across three distinct channels:
1. Pulse: Short-form video/trend oriented, high energy, visual.
2. Forum: Community discussion and Q&A focus, conversational.
3. ProNet: Professional B2B/career platform, value-driven, concise.

PUBLISHING CADENCE SPECIFICATION REQUIREMENT:
Your posting cadence MUST match the exact 3-post weekly execution calendar scope for this campaign:
- Pulse: 1 post/week (Peak window: 18:00)
- Forum: 1 post/week (Peak window: 14:00)
- ProNet: 1 post/week (Peak window: 09:00)
Total Weekly Posts: 3 (1 post per channel).

Your output must define clear target audience profiles, channel selection, content pillars, posting cadence dictionary, measurable KPIs, and testable strategic hypotheses.
When reviewing analytics feedback from previous weeks, you MUST integrate those concrete recommendations into your revised strategy.
"""

class StrategyAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="StrategyAgent",
            role="Campaign Strategy & Planning Lead",
            system_prompt=STRATEGY_SYSTEM_PROMPT
        )

    def execute(self, db: Session, campaign_id: str, payload: Dict[str, Any]) -> StrategyOutput:
        human_brief = payload.get("human_brief", "")
        week_number = payload.get("week_number", 1)
        analytics_recommendations = payload.get("analytics_recommendations", None)

        user_prompt = f"CAMPAIGN BRIEF:\n{human_brief}\n\nWEEK NUMBER: {week_number}"
        
        if week_number == 2 and analytics_recommendations:
            user_prompt += f"\n\nWEEK 1 ANALYTICS RECOMMENDATIONS (MUST INCORPORATE THESE INTO WEEK 2 STRATEGY):\n"
            for rec in analytics_recommendations:
                user_prompt += f"- [{rec.get('channel')}/{rec.get('category')}]: {rec.get('recommendation')} (Evidence: {rec.get('evidence')})\n"

        user_prompt += f"\n\nAVAILABLE CHANNELS & GUIDELINES:\n{settings.CHANNELS}"
        user_prompt += "\nFormulate a complete structured strategy."

        strategy_output = self.generate_structured(user_prompt, StrategyOutput, temperature=0.3)

        self.log_and_send(
            db=db,
            campaign_id=campaign_id,
            recipient="ContentAgent",
            message_type="STRATEGY_GENERATED",
            payload=strategy_output.model_dump(),
            action=f"Generated Strategy for Week {week_number}",
            input_summary=f"Brief: {human_brief[:100]}...",
            output_summary=f"Pillars: {', '.join(strategy_output.content_pillars)} | Channels: {', '.join(strategy_output.channels)}"
        )

        return strategy_output
