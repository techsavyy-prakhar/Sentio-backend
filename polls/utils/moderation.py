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

PROTECTED_GROUPS = {
    "muslim", "christian", "hindu", "jew", "jews",
    "gay", "lesbian", "trans", "transgender",
    "black", "white", "dalit", "brahmin",
}

EXCLUSION_PHRASES = {
    "ban", "banned", "remove", "kick out",
    "expel", "eliminate", "exclude",
    "should be banned", "should not be allowed",
}

def violates_protected_group_policy(text: str) -> bool:
    text = text.lower()

    if any(group in text for group in PROTECTED_GROUPS):
        if any(phrase in text for phrase in EXCLUSION_PHRASES):
            return True

    return False


def is_content_allowed(text: str) -> bool:
    if not text or not text.strip():
        return True
    if violates_protected_group_policy(text):
        logging.warning("Blocked protected-group exclusion content")
        return False

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
                return False

        return True

    except Exception as e:
        logging.error(f"Moderation API failure: {e}")
        return True  # fail open
