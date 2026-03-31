"""
main.py — Entrypoint for the Morning Brief newsletter pipeline.

Run locally:
    export PERPLEXITY_API_KEY=...
    export ANTHROPIC_API_KEY=...
    export GMAIL_USER=...
    export GMAIL_APP_PASSWORD=...
    export RECIPIENT_EMAIL=...
    python main.py
"""

import asyncio
import os
import sys

from newsletter.pipeline import run_pipeline
from mailer.sender import send_email


def _require_env(name: str) -> str:
    value = os.environ.get(name)
    if not value:
        print(f"ERROR: Required environment variable '{name}' is not set.", file=sys.stderr)
        sys.exit(1)
    return value


async def main() -> None:
    gmail_user = _require_env("GMAIL_USER")
    gmail_app_password = _require_env("GMAIL_APP_PASSWORD")
    recipient = _require_env("RECIPIENT_EMAIL")
    # Pipeline reads PERPLEXITY_API_KEY and ANTHROPIC_API_KEY itself
    _require_env("PERPLEXITY_API_KEY")
    _require_env("ANTHROPIC_API_KEY")

    html = await run_pipeline()

    send_email(
        html_content=html,
        gmail_user=gmail_user,
        gmail_app_password=gmail_app_password,
        recipient=recipient,
    )


if __name__ == "__main__":
    asyncio.run(main())
