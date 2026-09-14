from typing import Dict, Any, List
from sqlalchemy.orm import Session
from app.agents.base_agent import BaseAgent
from app.llm.schemas import CommunityResponseOutput
from app.database.models import PlatformCommentModel

COMMUNITY_SYSTEM_PROMPT = """You are the Community Manager Agent for a social media AI agency.
Your task is to review incoming comments from audience members on published social media posts.

CLASSIFICATION & ACTION RULES:
1. Sentiment Categories: positive, neutral, negative, question, complaint, sensitive.
2. Sensitivity & Escalation:
   - Flag is_sensitive = true IF the comment involves severe safety hazards, electrical shocks, toxic leakage, legal threats, or harassment.
   - For sensitive comments, DO NOT write a public automated reply. Explain the escalation reason so it goes to Human Support.
3. Automated Reply:
   - For positive/neutral comments: Write a warm, friendly, brand-consistent thank-you reply.
   - For general questions/complaints: Provide helpful, courteous information without making unverified promises.
"""

class CommunityAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="CommunityManagerAgent",
            role="Audience Engagement & Community Lead",
            system_prompt=COMMUNITY_SYSTEM_PROMPT
        )

    def execute(self, db: Session, campaign_id: str, payload: Dict[str, Any]) -> List[Dict[str, Any]]:
        comments = payload.get("comments", [])
        processed_results = []

        for comment_data in comments:
            comment_id = comment_data.get("id")
            author = comment_data.get("author")
            content = comment_data.get("content")

            # Fallback rule check for extreme keywords
            content_lower = content.lower()
            hard_sensitive = any(kw in content_lower for kw in ["shock", "fire", "exploded", "sue", "lawyer", "toxic", "injury"])

            user_prompt = f"USER COMMENT TO EVALUATE:\nAuthor: {author}\nComment: '{content}'\n\nAnalyze and output structured community response."

            try:
                response_obj = self.generate_structured(user_prompt, CommunityResponseOutput, temperature=0.2)
            except Exception as e:
                # Safe fallback if LLM fails
                response_obj = CommunityResponseOutput(
                    sentiment="sensitive" if hard_sensitive else "neutral",
                    is_sensitive=hard_sensitive,
                    response_draft=None if hard_sensitive else f"Hi {author}, thank you for sharing your thoughts with us!",
                    reasoning=f"Fallback parsing logic executed. Error: {e}"
                )

            if hard_sensitive:
                response_obj.is_sensitive = True
                response_obj.sentiment = "sensitive"

            # Update DB record if present
            db_comment = db.query(PlatformCommentModel).filter(PlatformCommentModel.id == comment_id).first()
            if db_comment:
                db_comment.sentiment = response_obj.sentiment
                db_comment.is_sensitive = response_obj.is_sensitive
                if response_obj.is_sensitive:
                    db_comment.response_status = "ESCALATED"
                    db_comment.community_response = "[ESCALATED TO HUMAN SUPPORT]: Sensitive inquiry regarding product safety/legal risk."
                else:
                    db_comment.response_status = "RESPONDED"
                    db_comment.community_response = response_obj.response_draft
                db.commit()

            processed_results.append({
                "comment_id": comment_id,
                "author": author,
                "content": content,
                "sentiment": response_obj.sentiment,
                "is_sensitive": response_obj.is_sensitive,
                "response": response_obj.response_draft,
                "status": "ESCALATED" if response_obj.is_sensitive else "RESPONDED"
            })

        self.log_and_send(
            db=db,
            campaign_id=campaign_id,
            recipient="Orchestrator",
            message_type="COMMUNITY_COMMENTS_PROCESSED",
            payload={"processed_comments": processed_results},
            action=f"Processed {len(processed_results)} incoming audience comments",
            input_summary=f"Evaluated comments from mock platform",
            output_summary=f"Responded: {sum(1 for c in processed_results if not c['is_sensitive'])}, Escalated: {sum(1 for c in processed_results if c['is_sensitive'])}"
        )

        return processed_results
