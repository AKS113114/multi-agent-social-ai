import random
from typing import List, Dict, Any

class AudienceSimulator:
    """
    Generates realistic audience comments based on post content and performance.
    Planting sensitive escalation triggers for Community Manager testing.
    """

    COMMENT_TEMPLATES = {
        "Pulse": [
            "Wait this looks sick! How much is it for students?",
            "Need this in my dorm asap 🔥",
            "Is the extraction actually good or does it taste burnt?",
            "Can you make iced lattes with this steam wand?",
            "Bro 100 bucks is still steep for a student budget 😭",
            "Ordered mine yesterday! How long does shipping take?",
            "Is the water tank detachable for easy cleaning?"
        ],
        "Forum": [
            "Honestly as a 3rd year engineering student, coffee is 90% of my bloodstream. Does this fit on a tiny desk?",
            "How does the boiler temperature stability hold up compared to a DeLonghi Dedica?",
            "Does it come with a unpressurized portafilter basket out of the box?",
            "Great price point, but how durable is the internal pump after 6 months of daily use?",
            "Can anyone confirm if the steam wand has enough power for microfoam latte art?",
            "Looks promising! What's the warranty coverage for student buyers?"
        ],
        "ProNet": [
            "Impressive value proposition for young professionals working from home.",
            "Solid design simplicity. What is your current distribution strategy across campus retail?",
            "Minimalist aesthetics. Is there an enterprise office bundle available?",
            "Good positioning on affordability without compromising core pressure specs."
        ]
    }

    SENSITIVE_TEMPLATES = [
        "WARNING: My unit sparked from the back outlet when I turned it on! Total fire hazard, who do I contact for legal liability?",
        "Extremely dangerous! The steam wand exploded pressurized hot water onto my hand and caused a burn!",
        "This machine gave me a mild electrical shock when touched with wet hands. Reporting to safety authorities."
    ]

    @classmethod
    def generate_comments_for_post(cls, channel: str, copy: str, comment_count: int, seed: int = 100) -> List[Dict[str, Any]]:
        rng = random.Random(seed + len(copy))
        templates = cls.COMMENT_TEMPLATES.get(channel, cls.COMMENT_TEMPLATES["Pulse"])
        
        comments = []
        author_names = ["alex_reads", "coffee_lover_99", "dev_sarah", "dorm_barista", "marcus_p", "hannah_m", "sam_tech", "elena_v"]

        for i in range(min(comment_count, 6)):
            # 1 in 8 chance to generate a sensitive comment if comment_count >= 3
            if i == 0 and comment_count >= 3 and rng.random() < 0.25:
                content = rng.choice(cls.SENSITIVE_TEMPLATES)
                sentiment = "sensitive"
                is_sensitive = True
            else:
                content = rng.choice(templates)
                sentiment = "question" if "?" in content else ("positive" if any(w in content.lower() for w in ["sick", "great", "sick", "solid", "love", "ordered"]) else "neutral")
                is_sensitive = False

            author = rng.choice(author_names) + str(rng.randint(10, 99))
            comments.append({
                "author": author,
                "content": content,
                "sentiment": sentiment,
                "is_sensitive": is_sensitive
            })

        return comments
