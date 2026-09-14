from typing import Dict, Any, List
from sqlalchemy.orm import Session
from app.agents.base_agent import BaseAgent
from app.config import settings

SCHEDULER_SYSTEM_PROMPT = """You are the Scheduler & Publishing Coordinator Agent.
Your job is to take approved campaign posts and place them into an optimal publishing calendar schedule across the campaign duration.

OPTIMAL PEAK WINDOWS:
- Pulse: 17:00 to 21:00
- Forum: 12:00 to 15:00 and 18:00 to 21:00
- ProNet: 08:00 to 11:00

Schedule posts evenly across the week avoiding clashing consecutive time slots on the same channel.
"""

class SchedulerAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="SchedulerAgent",
            role="Publishing & Calendar Coordinator",
            system_prompt=SCHEDULER_SYSTEM_PROMPT
        )

    def execute(self, db: Session, campaign_id: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        approved_posts = payload.get("approved_posts", [])
        week_number = payload.get("week_number", 1)

        scheduled_calendar = []
        for idx, post in enumerate(approved_posts):
            channel = post.get("channel", "Pulse")
            peak_hours = settings.CHANNELS.get(channel, {}).get("peak_hours", [18])
            
            # Select peak hour based on post index offset
            selected_hour = peak_hours[idx % len(peak_hours)]
            minute = "30" if idx % 2 == 1 else "00"
            scheduled_time = f"{selected_hour:02d}:{minute}"

            scheduled_calendar.append({
                "post_id": post.get("id"),
                "channel": channel,
                "scheduled_time": scheduled_time,
                "week_number": week_number,
                "format": post.get("format"),
                "hook": post.get("hook"),
                "copy": post.get("copy"),
                "cta": post.get("cta"),
                "hashtags": post.get("hashtags")
            })

        self.log_and_send(
            db=db,
            campaign_id=campaign_id,
            recipient="MockPlatform",
            message_type="CALENDAR_SCHEDULED",
            payload={"calendar": scheduled_calendar},
            action=f"Scheduled {len(scheduled_calendar)} posts for Week {week_number}",
            input_summary=f"Approved Posts: {len(approved_posts)}",
            output_summary=f"Created publishing calendar across Pulse, Forum, ProNet"
        )

        return {"calendar": scheduled_calendar}
