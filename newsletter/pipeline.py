"""
newsletter/pipeline.py — Orchestrator.

Runs all research agents in parallel, then calls the writer agent,
and returns the final HTML newsletter.
"""

import asyncio
import os
from datetime import date
from pathlib import Path
from agents.researcher import research
from agents.writer import write_newsletter
from config import TOPICS

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

FALLBACK_TEMPLATE = "No data available for this topic today."


async def _run_research(topic_key: str, prompt: str, api_key: str) -> tuple[str, str]:
    """Fetch research for one topic. Returns (topic_key, content)."""
    try:
        content = await research(prompt, api_key)
        print(f"  [OK] {topic_key}")
        return topic_key, content
    except Exception as exc:
        print(f"  [WARN] Research failed for '{topic_key}': {exc}")
        return topic_key, FALLBACK_TEMPLATE


async def run_pipeline() -> str:
    """
    Full pipeline: research (parallel) → write → return HTML.
    Reads API keys from environment variables.
    """
    perplexity_key = os.environ["PERPLEXITY_API_KEY"]
    anthropic_key = os.environ["ANTHROPIC_API_KEY"]

    # --- Research phase (parallel) ---
    print("Running research agents...")
    tasks = [
        _run_research(key, meta["prompt"], perplexity_key)
        for key, meta in TOPICS.items()
    ]
    results = await asyncio.gather(*tasks)
    research_results = dict(results)

    # --- Write phase ---
    print("Writing newsletter...")
    html = write_newsletter(research_results, TOPICS, anthropic_key)
    print("Newsletter written.")

    _save_outputs(research_results, html)

    return html
