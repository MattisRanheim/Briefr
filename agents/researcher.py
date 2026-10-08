"""
agents/researcher.py — Perplexity research agent.

Each call queries the Perplexity online model for a specific topic prompt.
Returns a plain-text summary with source URLs.
"""

import asyncio

import httpx
from config import (
    PERPLEXITY_MODEL,
    PERPLEXITY_MAX_TOKENS,
    PERPLEXITY_TEMPERATURE,
    PERPLEXITY_SYSTEM_PROMPT,
)

PERPLEXITY_URL = "https://api.perplexity.ai/chat/completions"
MAX_RETRIES = 4
RETRY_BASE_DELAY = 5.0  # seconds; doubles each retry


async def research(topic_prompt: str, api_key: str) -> str:
    """
    Query Perplexity for a single topic. Returns the assistant's response text.
    Raises httpx.HTTPStatusError on non-2xx responses.
    """
    payload = {
        "model": PERPLEXITY_MODEL,
        "messages": [
            {"role": "system", "content": PERPLEXITY_SYSTEM_PROMPT},
            {"role": "user", "content": topic_prompt},
        ],
        "max_tokens": PERPLEXITY_MAX_TOKENS,
        "temperature": PERPLEXITY_TEMPERATURE,
    }
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    async with httpx.AsyncClient() as client:
        for attempt in range(MAX_RETRIES + 1):
            response = await client.post(
                PERPLEXITY_URL, headers=headers, json=payload, timeout=90.0
            )
            # Parallel topic requests can trip Perplexity's rate limit; back off and retry.
            if response.status_code in (429, 503) and attempt < MAX_RETRIES:
                await asyncio.sleep(RETRY_BASE_DELAY * (2 ** attempt))
                continue
            response.raise_for_status()
            return response.json()["choices"][0]["message"]["content"]
