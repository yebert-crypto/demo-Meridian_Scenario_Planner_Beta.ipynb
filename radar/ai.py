"""
AI-powered signal classification and summarization using Claude.

Falls back to keyword matching if API key is not set.
"""
import os
import json
from typing import Optional

from radar.models import SignalType
from radar.monitors.news import classify_signal as keyword_classify

_client = None


def _get_client():
    global _client
    if _client is None:
        import anthropic
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            return None
        _client = anthropic.Anthropic(api_key=api_key)
    return _client


SIGNAL_TYPES_LIST = "\n".join(f"- {t.value}" for t in SignalType)

SYSTEM_PROMPT = f"""You are a business development intelligence analyst at a major law firm (Perkins Coie).
Your job is to analyze news articles about client companies and:
1. Classify the signal type
2. Write a concise 1-2 sentence summary focused on what is happening
3. Write a 1-sentence BD insight explaining why this matters for the law firm

Signal types to choose from:
{SIGNAL_TYPES_LIST}

Respond ONLY with valid JSON in this exact format:
{{
  "signal_type": "<exact signal type from list above>",
  "summary": "<1-2 sentences: what is actually happening>",
  "bd_insight": "<1 sentence: why this matters for Perkins Coie BD>"
}}"""


def classify_and_summarize(
    headline: str,
    body: str,
    company: str,
) -> tuple[SignalType, str, str]:
    """
    Returns (signal_type, summary, bd_insight).
    Falls back to keyword classify + raw headline if no API key.
    """
    client = _get_client()
    if not client:
        signal_type = keyword_classify(f"{headline} {body}")
        return signal_type, body[:200] if body else headline, ""

    try:
        message = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=300,
            system=SYSTEM_PROMPT,
            messages=[{
                "role": "user",
                "content": f"Company: {company}\nHeadline: {headline}\nArticle: {body[:800]}"
            }]
        )
        data = json.loads(message.content[0].text)
        signal_type = next(
            (t for t in SignalType if t.value == data.get("signal_type")),
            keyword_classify(f"{headline} {body}")
        )
        return signal_type, data.get("summary", headline), data.get("bd_insight", "")
    except Exception:
        signal_type = keyword_classify(f"{headline} {body}")
        return signal_type, body[:200] if body else headline, ""
