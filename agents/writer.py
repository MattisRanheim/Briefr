"""
agents/writer.py — Claude Haiku writer agent.

Takes each topic's deduplicated stories and synthesises them into a full
HTML newsletter.
"""

import anthropic
from config import WRITER_MODEL, WRITER_MAX_TOKENS, WRITER_SYSTEM_PROMPT


def _strip_code_fence(html: str) -> str:
    """Strip a markdown code fence if the model wrapped its output in one."""
    text = html.strip()
    if text.startswith("```"):
        text = text.split("\n", 1)[1] if "\n" in text else ""
        if text.endswith("```"):
            text = text.rsplit("```", 1)[0]
    return text.strip()


def build_user_message(topic_stories: dict, topics_meta: dict, today_display: str) -> str:
    """Build the user message passed to Claude, structured by topic."""
    sections = [
        f"Today's date: {today_display}\n\n"
        "Here are today's deduplicated stories. Write the Morning Brief newsletter."
    ]
    for key, stories in topic_stories.items():
        label = topics_meta[key]["label"]
        if not stories:
            sections.append(f"## {label}\nNO_NEW_DEVELOPMENTS")
            continue
        lines = [f"## {label}"]
        for story in stories:
            urls = ", ".join(story.get("source_urls", [])) or "none"
            lines.append(f"- {story['title']}: {story['summary']} (Source: {urls})")
        sections.append("\n".join(lines))
    return "\n\n".join(sections)


def write_newsletter(topic_stories: dict, topics_meta: dict, today_display: str, api_key: str) -> str:
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
                "content": build_user_message(topic_stories, topics_meta, today_display),
            }
        ],
    )
    if message.stop_reason == "max_tokens":
        print(
            f"  [WARN] Writer output was truncated by max_tokens ({WRITER_MAX_TOKENS}) "
            "— the newsletter HTML is likely incomplete/broken."
        )
    return _strip_code_fence(message.content[0].text)
