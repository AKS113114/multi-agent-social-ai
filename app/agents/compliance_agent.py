from typing import Dict, Any
from sqlalchemy.orm import Session
from app.agents.base_agent import BaseAgent
from app.llm.schemas import ComplianceOutput

COMPLIANCE_SYSTEM_PROMPT = """You are the Brand & Compliance Officer Agent for a social media AI agency.
Your task is to conduct strict compliance audits of social media post copy and creative briefs before publication.

COMPLIANCE AUDIT CRITERIA:
1. False Claims / Over-Promising: Check for exaggerated guarantees ("100% guaranteed", "overnight results", "instant miracle", false claims).
2. Brand Tone Consistency: Ensure copy matches brief instructions ("don't over-promise", "keep tone playful/professional").
3. Banned/Risky Phrases: Flag misleading, unsafe, deceptive, or offensive language.
4. Channel Format Rules:
   - Pulse: Copy must be under 60 words.
   - ProNet: Tone must not be excessively informal or slang-heavy.
5. Legal Risk: Flag any missing disclaimers for price claims or performance guarantees.

OUTPUT REQUIREMENT:
- approved: Set to true ONLY IF score >= 75 and no severe compliance violations exist.
- score: Numeric rating between 0 and 100.
- issues: List specific problems detected.
- required_changes: Explicit, actionable instructions for Content Agent to fix if rejected.
- reasoning: Detailed explanation.
"""

class ComplianceAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="ComplianceAgent",
            role="Brand Safety & Legal Compliance Officer",
            system_prompt=COMPLIANCE_SYSTEM_PROMPT
        )

    def execute(self, db: Session, campaign_id: str, payload: Dict[str, Any]) -> ComplianceOutput:
        post = payload.get("post", {})
        creative_brief = payload.get("creative_brief", {})
        campaign_brief = payload.get("campaign_brief", "")
        revision_count = payload.get("revision_count", 0)

        # Basic deterministic rule checks before calling LLM to catch blatant violations
        copy_text = post.get("copy", "").lower()
        channel = post.get("channel", "")
        word_count = len(post.get("copy", "").split())
        
        explicit_violations = []
        if "100% guarantee" in copy_text or "instant miracle" in copy_text:
            explicit_violations.append("Contains prohibited guarantee phrase ('100% guarantee' or 'instant miracle').")
        if channel == "Pulse" and word_count > 70:
            explicit_violations.append(f"Pulse channel copy length ({word_count} words) exceeds maximum limit of 60 words.")

        user_prompt = (
            f"ORIGINAL HUMAN BRIEF GUIDELINES:\n{campaign_brief}\n\n"
            f"POST COPY TO REVIEW:\n"
            f"Channel: {post.get('channel')}\n"
            f"Format: {post.get('format')}\n"
            f"Hook: {post.get('hook')}\n"
            f"Copy: {post.get('copy')}\n"
            f"CTA: {post.get('cta')}\n"
            f"Hashtags: {post.get('hashtags')}\n\n"
            f"CREATIVE BRIEF:\n"
            f"Visual Concept: {creative_brief.get('visual_concept')}\n"
            f"On-Screen Text: {creative_brief.get('on_screen_text')}\n"
        )
        if explicit_violations:
            user_prompt += f"\nPRE-AUDIT DETECTED ISSUES:\n- " + "\n- ".join(explicit_violations)

        user_prompt += "\nPerform a complete compliance audit and output structured evaluation."

        compliance_output = self.generate_structured(user_prompt, ComplianceOutput, temperature=0.1)

        # Force override if explicit pre-audit violation exists
        if explicit_violations:
            compliance_output.approved = False
            compliance_output.score = min(compliance_output.score, 40.0)
            compliance_output.issues.extend(explicit_violations)

        status_str = "APPROVED" if compliance_output.approved else "REJECTED"
        recipient = "Orchestrator" if compliance_output.approved else "ContentAgent"

        self.log_and_send(
            db=db,
            campaign_id=campaign_id,
            recipient=recipient,
            message_type="COMPLIANCE_REVIEW_COMPLETE",
            payload=compliance_output.model_dump(),
            action=f"Compliance Audit {status_str} (Score: {compliance_output.score}/100)",
            input_summary=f"Post for {post.get('channel')}, Revision Attempt #{revision_count}",
            output_summary=f"Status: {status_str}, Issues: {len(compliance_output.issues)}",
            status=status_str,
            revision_count=revision_count
        )

        return compliance_output
