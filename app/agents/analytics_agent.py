from typing import Dict, Any, List
from sqlalchemy.orm import Session
from app.agents.base_agent import BaseAgent
from app.llm.schemas import AnalyticsOutput

ANALYTICS_SYSTEM_PROMPT = """You are the Lead Performance & Analytics Agent for a social media AI agency.
Your task is to conduct deep performance reviews of completed social media campaigns based on empirical data from the mock social platform.

REQUIREMENTS FOR ANALYSIS & EVIDENCE QUALITY:
1. Compare start KPIs against actual performance metrics (impressions, engagement rate, comments, shares, saves, clicks, follower delta).
2. For EVERY recommendation, you MUST provide 5 structured fields:
   - observation: Direct metric observation comparing posts within the SAME channel or metric dimension.
   - evidence: Cite sample size (e.g., n=1 post per channel) and exact metric values of the SAME metric being optimized (e.g. comparing impressions to impressions, engagement rate to engagement rate). NEVER cite comments as evidence for an impression recommendation.
   - hypothesis: Plausible explanation for the observed metric difference.
   - confidence: MUST be "Low" (or "Low (n=1 sample)") for n=1 evidence. Use "Medium" ONLY when there is meaningful repeated comparable evidence. Use "High" ONLY for strong repeated evidence.
   - recommendation: Actionable instruction or "Insufficient evidence to change".

3. STRICT EVIDENCE & CONFIDENCE RULES:
   - Metric Alignment: Compare impressions to impressions, engagement rate to engagement rate. Do NOT claim causality from a different metric.
   - Within-Channel: Compare copy length, timing, and CTAs strictly WITHIN the same channel (e.g., Pulse posts vs Pulse posts). Do NOT compare Pulse to ProNet to infer copy length rules.
   - Small Sample Confidence Rating:
     * n=1 sample: MUST rate confidence as "Low" (or "Low (n=1 sample)").
     * n>=2 comparable samples: May rate confidence as "Medium".
     * Strong repeated samples: May rate confidence as "High".
   - Do NOT invent false causality or cross-channel assumptions.

Your recommendations will be fed directly into the Strategy Agent to drive Week 2 optimizations!
"""

class AnalyticsAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="AnalyticsAgent",
            role="Lead Data Analyst & Performance Architect",
            system_prompt=ANALYTICS_SYSTEM_PROMPT
        )

    def execute(self, db: Session, campaign_id: str, payload: Dict[str, Any]) -> AnalyticsOutput:
        week_number = payload.get("week_number", 1)
        kpis = payload.get("kpis", [])
        post_metrics = payload.get("post_metrics", [])
        comments_summary = payload.get("comments_summary", "")

        # Format metrics summary for prompt
        metrics_text = ""
        for pm in post_metrics:
            metrics_text += (
                f"- Post ID: {pm.get('id')}\n"
                f"  Channel: {pm.get('channel')}, Format: {pm.get('format')}, Scheduled Time: {pm.get('scheduled_time')}\n"
                f"  Hook: '{pm.get('hook')}'\n"
                f"  Copy Length: {len(pm.get('post_copy', '').split())} words, Hashtags Count: {len(pm.get('hashtags', []))}\n"
                f"  Impressions: {pm.get('impressions')}, Likes: {pm.get('likes')}, Comments: {pm.get('comments_count')}\n"
                f"  Shares: {pm.get('shares')}, Saves: {pm.get('saves')}, Clicks: {pm.get('clicks')}\n"
                f"  Engagement Rate: {pm.get('engagement_rate'):.2f}%\n\n"
            )

        user_prompt = (
            f"PERFORMANCE DATA FOR WEEK {week_number}:\n"
            f"Target KPIs: {kpis}\n\n"
            f"POST METRICS METADATA:\n{metrics_text}\n"
            f"AUDIENCE COMMENTS SENTIMENT SUMMARY:\n{comments_summary}\n\n"
            f"Perform a comprehensive performance audit and produce structured evidence-backed recommendations for Strategy."
        )

        analytics_output = self.generate_structured(user_prompt, AnalyticsOutput, temperature=0.2)

        self.log_and_send(
            db=db,
            campaign_id=campaign_id,
            recipient="Orchestrator",
            message_type="WEEKLY_ANALYTICS_REPORT",
            payload=analytics_output.model_dump(),
            action=f"Completed Weekly Analytics Report for Week {week_number}",
            input_summary=f"Analyzed {len(post_metrics)} posts for Week {week_number}",
            output_summary=f"Generated {len(analytics_output.recommendations)} concrete recommendations for Week 2"
        )

        return analytics_output
