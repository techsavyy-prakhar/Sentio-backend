from openai import OpenAI
from django.conf import settings

client = OpenAI(api_key=settings.OPENAI_API_KEY)
import json


def generate_themes(category):

    prompt = f"""
    Generate 5 trending discussion themes in category: {category}.
    Return JSON object:
    {{
      "themes": [
        {{
          "theme": "",
          "description": ""
        }}
      ]
    }}
    """

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        temperature=0.7,
        max_tokens=250,
        response_format={"type": "json_object"},
        messages=[{"role": "user", "content": prompt}],
    )

    return json.loads(response.choices[0].message.content)


def generate_polls(category, theme):

    prompt = f"""
    Generate 5 neutral Yes/No poll questions.

    Category: {category}
    Theme: {theme}

    Return JSON object:
    {{
      "polls": [
        {{
          "question": "",
          "description": ""
        }}
      ]
    }}
    """

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        temperature=0.7,
        max_tokens=350,
        response_format={"type": "json_object"},
        messages=[{"role": "user", "content": prompt}],
    )

    return json.loads(response.choices[0].message.content)
