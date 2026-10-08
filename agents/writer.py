"""
agents/writer.py — Editor + writer agent (Claude Sonnet).

Takes the raw research for every topic plus the recently-sent story log and
does the whole editorial job in one call: filter (aggressively) for
significance and novelty, write the newsletter, and report which stories
and explainer were used so they can be remembered for future dedup.
"""

import json
import re

import anthropic

from config import WRITER_MODEL, WRITER_MAX_TOKENS, WRITER_SYSTEM_PROMPT

RESEARCH_FAILED = "RESEARCH_FAILED"


def _strip_code_fence(text: str) -> str:
    """Strip a markdown code fence if the model wrapped its output in one."""
    text = text.strip()
    if text.startswith("```"):
        text = text.split("\n", 1)[1] if "\n" in text else ""
        if text.endswith("```"):
            text = text.rsplit("```", 1)[0]
    return text.strip()


def _format_history(stories: list[dict]) -> str:
    if not stories:
        return "(none)"
    return "\n".join(
        f"- [{s['last_seen']}] {s['title']} — {s['summary']}" for s in stories
    )


def build_user_message(
    research: dict,
    history: dict,
    topics_meta: dict,
    today_display: str,
) -> str:
    """Build the user message: per-topic sent history + raw research, then explainer history."""
    parts = [f"Today's date: {today_display}"]
    for key, meta in topics_meta.items():
        raw = research.get(key, RESEARCH_FAILED)
        parts.append(
            f"=== TOPIC KEY: {key} | {meta['label']} ===\n"
            f"Already sent in the last two weeks:\n{_format_history(history.get(key, []))}\n\n"
            f"Raw research from today:\n{raw}"
        )
    parts.append(
        "=== EXPLAINERS ALREADY SENT ===\n" + _format_history(history.get("explainers", []))
    )
    parts.append("Now edit and write today's Morning Brief.")
    return "\n\n".join(parts)


def parse_response(text: str) -> tuple[str, dict]:
    """Split the model output into (html, story_log). story_log is {} if unparseable."""
    html_match = re.search(r"<newsletter>(.*?)</newsletter>", text, re.DOTALL)
    if not html_match:
        raise ValueError("Writer output contained no <newsletter> block.")
    html = _strip_code_fence(html_match.group(1))

    story_log: dict = {}
    log_match = re.search(r"<story_log>(.*?)</story_log>", text, re.DOTALL)
    if log_match:
        try:
            parsed = json.loads(_strip_code_fence(log_match.group(1)))
            if isinstance(parsed, dict):
                story_log = parsed
        except json.JSONDecodeError as exc:
            print(f"  [WARN] Could not parse story_log JSON ({exc}); history not updated.")
    else:
        print("  [WARN] Writer output had no <story_log> block; history not updated.")
    return html, story_log


def write_newsletter(
    research: dict,
    history: dict,
    topics_meta: dict,
    today_display: str,
    api_key: str,
) -> tuple[str, dict]:
    """
    Call Claude Sonnet to filter, write and log. Returns (html, story_log).
    Raises anthropic.APIError on failure, ValueError if no newsletter was produced.
    """
    client = anthropic.Anthropic(api_key=api_key)
    message = client.messages.create(
        model=WRITER_MODEL,
        max_tokens=WRITER_MAX_TOKENS,
        system=WRITER_SYSTEM_PROMPT,
        messages=[
            {
                "role": "user",
                "content": build_user_message(research, history, topics_meta, today_display),
            }
        ],
    )
    if message.stop_reason == "max_tokens":
        print(
            f"  [WARN] Writer output was truncated by max_tokens ({WRITER_MAX_TOKENS}) "
            "— the newsletter HTML is likely incomplete/broken."
        )
    text = "".join(b.text for b in message.content if b.type == "text")
    return parse_response(text)
