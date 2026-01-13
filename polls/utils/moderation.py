from openai import OpenAI
from django.conf import settings
import logging

# ✅ Create client ONCE, with key
client = OpenAI(api_key=settings.OPENAI_API_KEY)

BLOCKED_CATEGORIES = {
    "sexual",
    "sexual_minors",
    "self_harm",
    "self_harm_instructions",
    "self_harm_intent",
    "violence",
    "violence_graphic",
    "hate",
    "hate_threatening",
    "harassment",
    "harassment_threatening",
    "extremism",
}

def is_content_allowed(text: str) -> bool:
    try:
        if not text:
            return True

        response = client.moderations.create(
            model="omni-moderation-latest",
            input=text,
        )

        result = response.results[0]
        for category, flagged in result.categories.items():
            if flagged and category in BLOCKED_CATEGORIES:
                return False

        for category, score in result.category_scores.items():
            if score >= 0.8 and category in BLOCKED_CATEGORIES:
                return False

        return True

    except Exception as e:
        logging.error(f"Moderation error: {e}")
        return False 
