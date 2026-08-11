"""
newsletter/state.py — Persisted story log.

Tracks which stories have already been sent, keyed by topic, so the dedupe
agent can compare against a rolling window of recent history. Unlike
output/ (git-ignored, ephemeral per CI run), state/seen_stories.json is
git-tracked — the workflow commits it back after each run so history
survives between GitHub Actions runs.
"""

import json
from datetime import date, datetime, timedelta
from pathlib import Path

STATE_DIR = Path(__file__).parent.parent / "state"
STATE_FILE = STATE_DIR / "seen_stories.json"


def load_state() -> dict:
    """Load the story log, or an empty one if it doesn't exist yet."""
    if not STATE_FILE.exists():
        return {}
    with open(STATE_FILE) as f:
        return json.load(f)


def save_state(state: dict) -> None:
    STATE_DIR.mkdir(exist_ok=True)
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=2, sort_keys=True)
        f.write("\n")


def get_recent_history(state: dict, topic_key: str, days: int) -> list[dict]:
    """Return stories for a topic last seen within the past `days` days."""
    cutoff = date.today() - timedelta(days=days)
    return [
        story
        for story in state.get(topic_key, [])
        if datetime.strptime(story["last_seen"], "%Y-%m-%d").date() >= cutoff
    ]


def update_state(state: dict, topic_key: str, kept_stories: list[dict], today: str) -> dict:
    """Upsert today's kept stories into the log for a topic."""
    existing = {s["id"]: s for s in state.get(topic_key, [])}
    for story in kept_stories:
        entry = existing.get(story["id"])
        if entry:
            entry["last_seen"] = today
            entry["title"] = story["title"]
            entry["summary"] = story["summary"]
        else:
            existing[story["id"]] = {
                "id": story["id"],
                "title": story["title"],
                "summary": story["summary"],
                "source_urls": story.get("source_urls", []),
                "first_seen": today,
                "last_seen": today,
            }
    state[topic_key] = list(existing.values())
    return state


def prune_state(state: dict, days: int) -> dict:
    """Drop stories not seen within the last `days` days, across all topics."""
    cutoff = date.today() - timedelta(days=days)
    for topic_key, stories in state.items():
        state[topic_key] = [
            s for s in stories
            if datetime.strptime(s["last_seen"], "%Y-%m-%d").date() >= cutoff
        ]
    return state
