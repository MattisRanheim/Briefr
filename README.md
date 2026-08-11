# Morning Brief

A daily newsletter delivered to your Gmail at 7:30am CET. Four parallel Perplexity research agents cover AI/LLMs, Data Science & ML, Quantitative Finance, and Scandinavian Tech & Entrepreneurship. Claude Haiku synthesises the results into a clean HTML email.

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

Copy `.env.example` to `.env` and fill in your credentials:

```bash
cp .env.example .env
# then open .env and add your values
```

`.env` is git-ignored and will never be committed. To load it and run:

```bash
pip install -r requirements.txt
set -a && source .env && set +a
python3 main.py
```

`set -a` exports every variable defined in the file so they're visible to the subprocess. `set +a` turns that off afterwards.

## Customisation

All topics and prompts live in [config.py](config.py). Edit `TOPICS` to add, remove, or rephrase topics. The writer's persona and HTML styles are in `WRITER_SYSTEM_PROMPT`.

## Duplicate-story detection

Raw research is parsed into discrete stories (`agents/extractor.py`), each given a
stable id based on its core entities/event rather than exact wording. Before writing,
each story is checked against `state/seen_stories.json` — up to `DEDUPE_WINDOW_DAYS`
(default 14) of story history per topic — and a Claude Haiku call (`agents/deduper.py`)
judges whether it's a genuine repeat or a real update on a known subject. Topics with
nothing new are written as one honest line instead of padding — that's expected on
slow news days, not a bug.

`state/seen_stories.json` is git-tracked (unlike `output/`, which is git-ignored) so
history survives between GitHub Actions runs: the workflow commits it back after
every send.

## Timezone note

The GitHub Actions cron runs in UTC. The workflow is set to `30 6 * * *` (7:30 CET, UTC+1). During summer (CEST, UTC+2) you'll receive it at 8:30 — update the cron to `30 5 * * *` for summer delivery at 7:30.
