"""
agents/writer.py — Claude Haiku writer agent.

Takes all research results and synthesises them into a full HTML newsletter.
"""

import anthropic
from config import WRITER_MODEL, WRITER_MAX_TOKENS, WRITER_SYSTEM_PROMPT


def build_user_message(research_results: dict, topics_meta: dict) -> str:
    """Build the user message passed to Claude, structured by topic."""
    sections = ["Here are today's research summaries. Write the Morning Brief newsletter.\n"]
    for key, content in research_results.items():
        label = topics_meta[key]["label"]
        sections.append(f"## {label}\n{content}")
    return "\n\n".join(sections)


def write_newsletter(research_results: dict, topics_meta: dict, api_key: str) -> str:
    """
    Call Claude Haiku to produce the HTML newsletter.
    Returns the full HTML string.
    Raises anthropic.APIError on failure.
    """
    client = anthropic.Anthropic(api_key=api_key)
    message = client.messages.create(
        model=WRITER_MODEL,
        max_tokens=WRITER_MAX_TOKENS,
        system=WRITER_SYSTEM_PROMPT,
        messages=[
            {
                "role": "user",
                "content": build_user_message(research_results, topics_meta),
            }
        ],
    )
    return message.content[0].text
