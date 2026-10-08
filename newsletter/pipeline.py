"""
newsletter/pipeline.py — Orchestrator.

Runs all research agents in parallel, then hands the raw research plus the
recently-sent story log to a single editor/writer call that filters (for
significance and novelty), writes the newsletter, and reports which stories
it used. The story log is persisted for future dedup.
"""

import asyncio
import os
from datetime import date
from pathlib import Path

from agents.researcher import research
from agents.writer import write_newsletter, RESEARCH_FAILED
from config import TOPICS, DEDUPE_WINDOW_DAYS
from newsletter.state import (
    load_state,
    save_state,
    get_recent_history,
    update_state,
    prune_state,
)

OUTPUT_DIR = Path(__file__).parent.parent / "output"



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
        return topic_key, RESEARCH_FAILED


def _valid_story(story) -> bool:
    return isinstance(story, dict) and all(
        isinstance(story.get(k), str) and story[k] for k in ("id", "title", "summary")
    )


async def run_pipeline() -> str:
    """
    Full pipeline: research (parallel) → edit + write (one Sonnet call) →
    persist story log → return HTML.
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

    # --- Edit + write phase ---
    print("Editing and writing newsletter...")
    history = {
        key: get_recent_history(state, key, DEDUPE_WINDOW_DAYS)
        for key in [*TOPICS, "explainers"]
    }
    html, story_log = write_newsletter(
        research_results,
        history,
        TOPICS,
        date.today().strftime("%B %d, %Y"),
        anthropic_key,
    )
    print("Newsletter written.")

    # --- Persist story log ---
    for key in TOPICS:
        stories = [s for s in story_log.get(key, []) if _valid_story(s)]
        print(f"  [OK] {key}: {len(stories)} stories sent")
        state = update_state(state, key, stories, today)
    explainer = story_log.get("explainer")
    if _valid_story(explainer):
        print(f"  [OK] explainer: {explainer['title']}")
        state = update_state(state, "explainers", [explainer], today)
    state = prune_state(state, DEDUPE_WINDOW_DAYS)
    save_state(state)

    _save_outputs(research_results, html)

    return html
