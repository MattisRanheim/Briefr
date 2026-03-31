"""
newsletter/pipeline.py — Orchestrator.

Runs all research agents in parallel, then calls the writer agent,
and returns the final HTML newsletter.
"""

import asyncio
import os
from agents.researcher import research
from agents.writer import write_newsletter
from config import TOPICS

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

    return html
