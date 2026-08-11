"""
newsletter/pipeline.py — Orchestrator.

Runs all research agents in parallel, extracts discrete stories from each
topic's raw research, filters out stories already sent in the last
DEDUPE_WINDOW_DAYS days, writes the newsletter, and persists the updated
story log for future runs.
"""

import asyncio
import os
from datetime import date
from pathlib import Path

from agents.researcher import research
from agents.extractor import extract_stories
from agents.deduper import dedupe_stories
from agents.writer import write_newsletter
from config import TOPICS, DEDUPE_WINDOW_DAYS
from newsletter.state import (
    load_state,
    save_state,
    get_recent_history,
    update_state,
    prune_state,
)

OUTPUT_DIR = Path(__file__).parent.parent / "output"

FALLBACK_TEMPLATE = "No data available for this topic today."


def _save_outputs(research_results: dict, html: str) -> None:
    OUTPUT_DIR.mkdir(exist_ok=True)
    today = date.today().isoformat()

    research_path = OUTPUT_DIR / f"{today}_research.txt"
    with open(research_path, "w") as f:
        for key, content in research_results.items():
            label = TOPICS[key]["label"]
            f.write(f"{'='*60}\n{label}\n{'='*60}\n{content}\n\n")
    print(f"  Research saved → {research_path}")

    html_path = OUTPUT_DIR / f"{today}_newsletter.html"
    with open(html_path, "w") as f:
        f.write(html)
    print(f"  Newsletter saved → {html_path}")


async def _run_research(topic_key: str, prompt: str, api_key: str) -> tuple[str, str]:
    """Fetch research for one topic. Returns (topic_key, content)."""
    try:
        content = await research(prompt, api_key)
        print(f"  [OK] {topic_key}")
        return topic_key, content
    except Exception as exc:
        print(f"  [WARN] Research failed for '{topic_key}': {exc}")
        return topic_key, FALLBACK_TEMPLATE


async def _extract_and_dedupe(
    topic_key: str,
    topic_label: str,
    raw_text: str,
    history: list[dict],
    anthropic_key: str,
) -> tuple[str, list[dict]]:
    """Extract discrete stories from raw research, then drop ones already sent recently."""
    if raw_text == FALLBACK_TEMPLATE:
        return topic_key, []

    try:
        candidates = await extract_stories(topic_label, raw_text, anthropic_key)
    except Exception as exc:
        print(f"  [WARN] Extraction failed for '{topic_key}': {exc}")
        return topic_key, []

    if not candidates:
        print(f"  [OK] {topic_key}: no stories extracted")
        return topic_key, []

    if not history:
        print(f"  [OK] {topic_key}: {len(candidates)} new (no history to compare)")
        return topic_key, candidates

    try:
        kept = await dedupe_stories(topic_label, candidates, history, anthropic_key)
    except Exception as exc:
        print(f"  [WARN] Dedup failed for '{topic_key}', keeping all candidates: {exc}")
        return topic_key, candidates

    print(f"  [OK] {topic_key}: {len(kept)}/{len(candidates)} kept after dedup")
    return topic_key, kept


async def run_pipeline() -> str:
    """
    Full pipeline: research (parallel) → extract + dedupe (parallel) →
    write → persist story log → return HTML.
    Reads API keys from environment variables.
    """
    perplexity_key = os.environ["PERPLEXITY_API_KEY"]
    anthropic_key = os.environ["ANTHROPIC_API_KEY"]
    today = date.today().isoformat()

    state = load_state()

    # --- Research phase (parallel) ---
    print("Running research agents...")
    research_tasks = [
        _run_research(key, meta["prompt"], perplexity_key)
        for key, meta in TOPICS.items()
    ]
    research_results = dict(await asyncio.gather(*research_tasks))

    # --- Extraction + dedup phase (parallel) ---
    print("Extracting and deduplicating stories...")
    dedupe_tasks = [
        _extract_and_dedupe(
            key,
            TOPICS[key]["label"],
            research_results[key],
            get_recent_history(state, key, DEDUPE_WINDOW_DAYS),
            anthropic_key,
        )
        for key in TOPICS
    ]
    topic_stories = dict(await asyncio.gather(*dedupe_tasks))

    # --- Persist story log ---
    for key, stories in topic_stories.items():
        state = update_state(state, key, stories, today)
    state = prune_state(state, DEDUPE_WINDOW_DAYS)
    save_state(state)

    # --- Write phase ---
    print("Writing newsletter...")
    html = write_newsletter(topic_stories, TOPICS, anthropic_key)
    print("Newsletter written.")

    _save_outputs(research_results, html)

    return html
