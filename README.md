# Morning Brief

A daily newsletter delivered to your Gmail at 7:30am CET. Four parallel Perplexity research agents cover AI/LLMs, Data Science & ML, Quantitative Finance, and Swedish Tech. Claude Haiku synthesises the results into a clean HTML email.

## Setup

### 1. Fork / clone this repo

### 2. Add GitHub Secrets

Go to **Settings → Secrets and variables → Actions** and add:

| Secret | Value |
|---|---|
| `PERPLEXITY_API_KEY` | From [perplexity.ai](https://perplexity.ai) |
| `ANTHROPIC_API_KEY` | From [console.anthropic.com](https://console.anthropic.com) |
| `GMAIL_USER` | Your full Gmail address |
| `GMAIL_APP_PASSWORD` | 16-char app password from [Google Account](https://myaccount.google.com/apppasswords) (requires 2FA) |
| `RECIPIENT_EMAIL` | Destination address (can be same as `GMAIL_USER`) |

### 3. Trigger manually to test

Go to **Actions → Morning Newsletter → Run workflow**.

## Local testing

```bash
pip install -r requirements.txt

export PERPLEXITY_API_KEY=...
export ANTHROPIC_API_KEY=...
export GMAIL_USER=...
export GMAIL_APP_PASSWORD=...
export RECIPIENT_EMAIL=...

python main.py
```

## Customisation

All topics and prompts live in [config.py](config.py). Edit `TOPICS` to add, remove, or rephrase topics. The writer's persona and HTML styles are in `WRITER_SYSTEM_PROMPT`.

## Timezone note

The GitHub Actions cron runs in UTC. The workflow is set to `30 6 * * *` (7:30 CET, UTC+1). During summer (CEST, UTC+2) you'll receive it at 8:30 — update the cron to `30 5 * * *` for summer delivery at 7:30.
