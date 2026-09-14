from typing import Dict, Any, List

class HiddenSignalsEngine:
    """
    Ground truth simulator engagement rules planted to evaluate Analytics Agent discovery capabilities.
    Analytics Agent does NOT have access to this class directly.
    """
    
    @staticmethod
    def calculate_signal_multipliers(
        channel: str,
        scheduled_time: str,
        format_type: str,
        copy: str,
        cta: str,
        hashtags: List[str],
        previous_formats: List[str],
        content_pillar: str,
        target_audience_keywords: List[str]
    ) -> Dict[str, float]:
        
        multipliers = {
            "reach": 1.0,
            "engagement": 1.0,
            "comment_rate": 1.0,
            "share_rate": 1.0,
            "click_rate": 1.0
        }

        # -------------------------------------------------------------
        # SIGNAL 1: Channel Peak Window Multiplier
        # -------------------------------------------------------------
        try:
            hour = int(scheduled_time.split(":")[0])
        except (ValueError, AttributeError, IndexError):
            hour = 12

        if channel == "Pulse":
            if 17 <= hour <= 21:
                multipliers["reach"] *= 1.45
            else:
                multipliers["reach"] *= 0.70
        elif channel == "Forum":
            if (12 <= hour <= 15) or (18 <= hour <= 21):
                multipliers["reach"] *= 1.40
            else:
                multipliers["reach"] *= 0.75
        elif channel == "ProNet":
            if 8 <= hour <= 11:
                multipliers["reach"] *= 1.50
            else:
                multipliers["reach"] *= 0.65

        # -------------------------------------------------------------
        # SIGNAL 2: Question CTA Boost for Comments
        # -------------------------------------------------------------
        combined_text = f"{copy} {cta}".strip()
        if combined_text.endswith("?") or "?" in cta:
            multipliers["comment_rate"] *= 1.65
            multipliers["engagement"] *= 1.15

        # -------------------------------------------------------------
        # SIGNAL 3: Copy Length Suitability
        # -------------------------------------------------------------
        word_count = len(copy.split())
        if channel == "Pulse":
            if word_count <= 60:
                multipliers["reach"] *= 1.20
            else:
                multipliers["reach"] *= 0.60
        elif channel == "Forum":
            if 40 <= word_count <= 120:
                multipliers["reach"] *= 1.25
            elif word_count < 30:
                multipliers["reach"] *= 0.70
        elif channel == "ProNet":
            if 60 <= word_count <= 160:
                multipliers["reach"] *= 1.30
            elif word_count < 40:
                multipliers["reach"] *= 0.75

        # -------------------------------------------------------------
        # SIGNAL 4: Hashtag Non-Linear Scaling
        # -------------------------------------------------------------
        tag_count = len(hashtags) if hashtags else 0
        if 1 <= tag_count <= 3:
            multipliers["reach"] *= 1.20
        elif tag_count == 0:
            multipliers["reach"] *= 0.90
        elif tag_count >= 5:
            multipliers["reach"] *= 0.70 # Hashtag clutter penalty

        # -------------------------------------------------------------
        # SIGNAL 5: Tone-Channel Resonance
        # -------------------------------------------------------------
        copy_lower = copy.lower()
        informal_keywords = ["bruh", "bro", "lol", "super cool", "lit", "vibes", "fire 💥"]
        energetic_keywords = ["launch", "epic", "huge", "unbelievable", "watch this", "must have"]

        if channel == "ProNet":
            if any(kw in copy_lower for kw in informal_keywords):
                multipliers["reach"] *= 0.65
                multipliers["engagement"] *= 0.75
            else:
                multipliers["reach"] *= 1.15

        if channel == "Pulse":
            if any(kw in copy_lower for kw in energetic_keywords):
                multipliers["reach"] *= 1.30
                multipliers["engagement"] *= 1.20

        # -------------------------------------------------------------
        # SIGNAL 6: Novelty Decay (Repeated Formats)
        # -------------------------------------------------------------
        if previous_formats and len(previous_formats) >= 2:
            if previous_formats[-1] == format_type and previous_formats[-2] == format_type:
                multipliers["reach"] *= 0.75
                multipliers["engagement"] *= 0.80

        # -------------------------------------------------------------
        # SIGNAL 7: Pillar-Audience Alignment
        # -------------------------------------------------------------
        pillar_lower = (content_pillar or "").lower()
        if any(kw.lower() in pillar_lower for kw in target_audience_keywords):
            multipliers["engagement"] *= 1.35
            multipliers["click_rate"] *= 1.40

        return multipliers
