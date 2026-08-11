"""
agents/deduper.py — Deduplication agent (Claude Haiku).

Compares today's candidate stories for a topic against that topic's recent
story history and returns only the candidates that are genuinely new —
letting the model judge "same event reported again" vs. "real update on a
known subject" rather than relying on exact-text or URL matching.
"""

import json
import anthropic
from config import DEDUPE_MODEL, DEDUPE_MAX_TOKENS, DEDUPE_SYSTEM_PROMPT


def _parse_id_list(text: str) -> set[str]:
    text = text.strip()
    if text.startswith("```"):
        text = text.strip("`")
        if text.startswith("json"):
            text = text[4:]
    text = text.strip()
    if not text:
        return set()
    data = json.loads(text)
    return set(data) if isinstance(data, list) else set()


def _format_stories(stories: list[dict]) -> str:
    return "\n".join(
        f"- id: {s['id']}\n  title: {s['title']}\n  summary: {s['summary']}"
        for s in stories
    )


async def dedupe_stories(
    topic_label: str,
    candidates: list[dict],
    history: list[dict],
    api_key: str,
) -> list[dict]:
    """
    Call Claude Haiku to filter out candidates that duplicate recently-sent
    stories. Returns the subset of `candidates` that should be kept.
    Raises anthropic.APIError or json.JSONDecodeError on failure.
    """
    user_message = (
        f"Topic: {topic_label}\n\n"
        f"Stories already sent in the last two weeks:\n{_format_stories(history)}\n\n"
        f"Today's candidate stories:\n{_format_stories(candidates)}"
    )
    client = anthropic.AsyncAnthropic(api_key=api_key)
    message = await client.messages.create(
        model=DEDUPE_MODEL,
        max_tokens=DEDUPE_MAX_TOKENS,
        system=DEDUPE_SYSTEM_PROMPT,
        messages=[{"role": "user", "content": user_message}],
    )
    kept_ids = _parse_id_list(message.content[0].text)
    return [s for s in candidates if s["id"] in kept_ids]
