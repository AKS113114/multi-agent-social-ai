import math
import random
from typing import Dict, Any, List
from app.simulator.hidden_rules import HiddenSignalsEngine

class EngagementSimulator:
    """
    Deterministic engagement calculation engine with controlled noise.
    Uses hidden rules multipliers + baseline metrics model.
    """

    BASE_METRICS = {
        "Pulse": {"base_impressions": 5000, "like_rate": 0.06, "comment_rate": 0.012, "share_rate": 0.025, "click_rate": 0.015},
        "Forum": {"base_impressions": 3200, "like_rate": 0.045, "comment_rate": 0.038, "share_rate": 0.012, "click_rate": 0.022},
        "ProNet": {"base_impressions": 2400, "like_rate": 0.035, "comment_rate": 0.018, "share_rate": 0.018, "click_rate": 0.035}
    }

    @classmethod
    def simulate_post_engagement(
        cls,
        channel: str,
        scheduled_time: str,
        format_type: str,
        copy: str,
        cta: str,
        hashtags: List[str],
        previous_formats: List[str] = None,
        content_pillar: str = "",
        target_audience_keywords: List[str] = None,
        seed: int = 42
    ) -> Dict[str, Any]:

        if target_audience_keywords is None:
            target_audience_keywords = ["budget", "student", "espresso", "price", "coffee"]
        if previous_formats is None:
            previous_formats = []

        base = cls.BASE_METRICS.get(channel, cls.BASE_METRICS["Pulse"])

        # Calculate ground-truth signal multipliers
        signals = HiddenSignalsEngine.calculate_signal_multipliers(
            channel=channel,
            scheduled_time=scheduled_time,
            format_type=format_type,
            copy=copy,
            cta=cta,
            hashtags=hashtags or [],
            previous_formats=previous_formats,
            content_pillar=content_pillar,
            target_audience_keywords=target_audience_keywords
        )

        # Use seeded RNG for reproducible controlled noise (±5%)
        rng = random.Random(seed + len(copy) + len(scheduled_time))
        noise = lambda: rng.uniform(0.95, 1.05)

        impressions = int(base["base_impressions"] * signals["reach"] * noise())
        likes = int(impressions * base["like_rate"] * signals["engagement"] * noise())
        comments_count = max(1, int(impressions * base["comment_rate"] * signals["comment_rate"] * noise()))
        shares = int(impressions * base["share_rate"] * signals["share_rate"] * noise())
        saves = int(likes * 0.25 * noise())
        clicks = int(impressions * base["click_rate"] * signals["click_rate"] * noise())
        follower_delta = int((likes * 0.05 + shares * 0.15 + saves * 0.1) * noise())

        total_engagements = likes + comments_count + shares + saves + clicks
        engagement_rate = round((total_engagements / max(1, impressions)) * 100, 2)

        return {
            "impressions": max(100, impressions),
            "likes": max(0, likes),
            "comments_count": max(1, comments_count),
            "shares": max(0, shares),
            "saves": max(0, saves),
            "clicks": max(0, clicks),
            "follower_delta": max(0, follower_delta),
            "engagement_rate": engagement_rate,
            "signals_applied": signals
        }
