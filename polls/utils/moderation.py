from openai import OpenAI
from django.conf import settings
import logging

client = OpenAI(api_key=settings.OPENAI_API_KEY)

HARD_BLOCK_CATEGORIES = {
    "sexual_minors",
    "violence_graphic",
    "self_harm_instructions",
    "self_harm_intent",
    "hate_threatening",
    "harassment_threatening",
    "extremism",
}

CONFIDENCE_THRESHOLD = 0.85  

def is_content_allowed(text: str) -> bool:
    if not text or not text.strip():
        return True

    try:
        response = client.moderations.create(
            model="omni-moderation-latest",
            input=text,
        )

        result = response.results[0]

        for category in HARD_BLOCK_CATEGORIES:
            if (
                result.categories.get(category) is True
                and result.category_scores.get(category, 0) >= CONFIDENCE_THRESHOLD
            ):
                return False

        return True

    except Exception as e:
        logging.error(f"Moderation API failure: {e}")
        return True
