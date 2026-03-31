"""
agents/researcher.py — Perplexity research agent.

Each call queries the Perplexity online model for a specific topic prompt.
Returns a plain-text summary with source URLs.
"""

import httpx
from config import (
    PERPLEXITY_MODEL,
    PERPLEXITY_MAX_TOKENS,
    PERPLEXITY_TEMPERATURE,
    PERPLEXITY_SYSTEM_PROMPT,
)

PERPLEXITY_URL = "https://api.perplexity.ai/chat/completions"


async def research(topic_prompt: str, api_key: str) -> str:
    """
    Query Perplexity for a single topic. Returns the assistant's response text.
    Raises httpx.HTTPStatusError on non-2xx responses.
    """
    async with httpx.AsyncClient() as client:
        response = await client.post(
            PERPLEXITY_URL,
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            json={
                "model": PERPLEXITY_MODEL,
                "messages": [
                    {"role": "system", "content": PERPLEXITY_SYSTEM_PROMPT},
                    {"role": "user", "content": topic_prompt},
                ],
                "max_tokens": PERPLEXITY_MAX_TOKENS,
                "temperature": PERPLEXITY_TEMPERATURE,
            },
            timeout=30.0,
        )
        response.raise_for_status()
        data = response.json()
        return data["choices"][0]["message"]["content"]
