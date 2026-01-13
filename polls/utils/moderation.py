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
            flagged = getattr(result.categories, category, False)
            score = getattr(result.category_scores, category, 0.0)

            if flagged and score >= threshold:
                logging.warning(
                    f"Blocked content | category={category} | score={score}"
                )
                return False

        return True

    except Exception as e:
        logging.error(f"Moderation API failure: {e}")
        return True  # fail open (Apple-safe)
