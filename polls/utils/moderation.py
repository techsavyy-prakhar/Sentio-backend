from openai import OpenAI
from django.conf import settings
import logging

client = OpenAI(api_key=settings.OPENAI_API_KEY)

CATEGORY_THRESHOLDS = {
    "sexual_minors": 0.80,
    "violence_graphic": 0.80,
    "self_harm_instructions": 0.75,
    "self_harm_intent": 0.75,
    "hate_threatening": 0.60,
    "harassment_threatening": 0.60,
    "extremism": 0.70,
}


def is_content_allowed(text: str) -> bool:
    if not text or not text.strip():
        return True

    try:
        response = client.moderations.create(
            model="omni-moderation-latest",
            input=text,
        )

        result = response.results[0]

        for category, threshold in CATEGORY_THRESHOLDS.items():
            if (
                result.categories.get(category) is True
                and result.category_scores.get(category, 0) >= threshold
            ):
                return False

        return True

    except Exception as e:
        logging.error(f"Moderation API failure: {e}")
        return True
