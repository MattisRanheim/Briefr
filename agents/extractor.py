"""
agents/extractor.py — Story extraction agent (Claude Haiku).

Parses a raw Perplexity research blob into a list of discrete, atomic
stories with a stable canonical id per story, so downstream dedup can
compare individual stories rather than whole-topic prose blobs.
"""

import json
import anthropic
from config import EXTRACTOR_MODEL, EXTRACTOR_MAX_TOKENS, EXTRACTOR_SYSTEM_PROMPT


def _parse_json_array(text: str) -> list[dict]:
    text = text.strip()
    if text.startswith("```"):
        text = text.strip("`")
        if text.startswith("json"):
            text = text[4:]
    text = text.strip()
    if not text:
        return []
    data = json.loads(text)
    return data if isinstance(data, list) else []


async def extract_stories(topic_label: str, raw_text: str, api_key: str) -> list[dict]:
    """
    Call Claude Haiku to parse raw research text into discrete stories.
    Returns a list of {id, title, summary, source_urls} dicts.
    Raises anthropic.APIError or json.JSONDecodeError on failure.
    """
    client = anthropic.AsyncAnthropic(api_key=api_key)
    message = await client.messages.create(
        model=EXTRACTOR_MODEL,
        max_tokens=EXTRACTOR_MAX_TOKENS,
        system=EXTRACTOR_SYSTEM_PROMPT,
        messages=[{"role": "user", "content": f"Topic: {topic_label}\n\n{raw_text}"}],
    )
    return _parse_json_array(message.content[0].text)
