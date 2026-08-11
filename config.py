"""
config.py — Topic definitions, prompt templates, and constants.
Edit this file to change topics, prompts, or newsletter style.
"""

# ---------------------------------------------------------------------------
# Research topics & prompts
# ---------------------------------------------------------------------------

TOPICS = {
    "ai_llms": {
        "label": "AI / LLMs",
        "prompt": (
            "Search for the most significant AI and LLM developments from the last 24 hours. "
            "Focus on: new model releases, research breakthroughs, major product launches, "
            "and industry news. Prioritise sources like The Verge, Ars Technica, Hugging Face blog, "
            "Import AI newsletter, and top AI research labs (OpenAI, Anthropic, Google DeepMind, Meta AI). "
            "Return 5–7 key developments. For each item include: a clear title, a substantive explanation "
            "(2–4 sentences covering what it is, why it matters, and any technical detail worth knowing), "
            "and one or more source URLs."
        ),
    },
    "data_science_ml": {
        "label": "Data Science & ML",
        "prompt": (
            "Search for the most interesting Data Science and Machine Learning developments "
            "from the last 24–48 hours. Focus on: new techniques, open-source tools and libraries, "
            "notable papers, Kaggle competitions, and practical ML engineering insights. "
            "Prioritise sources like Towards Data Science, fast.ai blog, Papers With Code, "
            "and ML Twitter/X. Return 5–7 items. For each include: a clear title, a substantive "
            "explanation (2–4 sentences covering what it is, why it's useful, and any key results or "
            "benchmarks), and one or more source URLs."
        ),
    },
    "quant_finance": {
        "label": "Quantitative Finance",
        "prompt": (
            "Search for the most relevant quantitative finance and financial markets news "
            "from the last 24 hours. Focus on: macro developments, derivatives and risk "
            "management insights, quant research, notable market moves, and fintech. "
            "Prioritise sources like Quantocracy, SSRN new working papers, Risk.net, "
            "FT Markets, and Bloomberg. Return 5–7 items. For each include: a clear title, a substantive "
            "explanation (2–4 sentences covering the development, its market implications, and any "
            "quantitative detail worth noting), and one or more source URLs."
        ),
    },
    "swedish_tech": {
        "label": "Swedish Tech & Entrepreneurship",
        "prompt": (
            "Search for the latest news in Swedish tech startups and entrepreneurship "
            "from the last 24–48 hours. Focus on: funding rounds, notable product launches, "
            "founder stories, ecosystem developments, and policy changes relevant to Swedish tech. "
            "Prioritise sources like Breakit, DI Digital, Sifted (Nordics), and TechCrunch Europe. "
            "Return 5–7 items. For each include: a clear title, a substantive explanation "
            "(2–4 sentences covering what happened, who is involved, and why it matters for the "
            "Swedish/Nordic ecosystem), and one or more source URLs."
        ),
    },
}

# ---------------------------------------------------------------------------
# Perplexity API settings
# ---------------------------------------------------------------------------

PERPLEXITY_MODEL = "sonar-pro"
PERPLEXITY_MAX_TOKENS = 1536
PERPLEXITY_TEMPERATURE = 0.2
PERPLEXITY_SYSTEM_PROMPT = (
    "You are a research assistant. Return structured, factual summaries with source URLs. "
    "Be concise but informative."
)

# ---------------------------------------------------------------------------
# Story extraction & deduplication (Claude Haiku) settings
# ---------------------------------------------------------------------------

# How many days of story history to compare new candidates against.
DEDUPE_WINDOW_DAYS = 14

EXTRACTOR_MODEL = "claude-haiku-4-5-20251001"
EXTRACTOR_MAX_TOKENS = 1024

EXTRACTOR_SYSTEM_PROMPT = """\
You parse a research summary into discrete, atomic news stories.

Return ONLY a JSON array (no prose, no markdown fences). Each element:
{
  "id": "short-kebab-case-slug",
  "title": "one-line headline",
  "summary": "1-2 sentence factual summary",
  "source_urls": ["https://..."]
}

Rules for "id":
- Build it from the core entities + event (e.g. "deepseek-v4-launch",
  "gemini-3-1-pro-arc-agi-score"), not from the outlet or exact wording.
- It must stay the same if the same underlying event were reported again in
  different words or by a different source.
- Lowercase, hyphen-separated, no dates, 2-6 words.

If the input contains no concrete stories (e.g. it's an apology, a refusal,
or says no news was found), return an empty JSON array: []
"""

DEDUPE_MODEL = "claude-haiku-4-5-20251001"
DEDUPE_MAX_TOKENS = 512

DEDUPE_SYSTEM_PROMPT = """\
You compare today's candidate stories against stories already sent to the
reader in the last two weeks, and decide which candidates are genuinely new.

Return ONLY a JSON array of the "id" values (from today's candidates) that
should be KEPT. Omit the rest — no prose, no markdown fences.

Drop a candidate if it reports the same underlying event as a previously-sent
story, even if reworded, sourced differently, or synthesized from a different
angle — e.g. "GPT-5.3 launches" reported again a few days later with no new
information.

Keep a candidate if it reports genuine new information about a
previously-covered subject — e.g. a new benchmark result, a follow-up
funding round, an updated price or metric, a concrete escalation of an
ongoing story. When genuinely unsure whether it's new information or a
rehash, drop it — the reader prefers fewer, meaningfully new items over
repeats, and an empty section is fine if nothing new happened.
"""

# ---------------------------------------------------------------------------
# Writer (Claude Haiku) settings
# ---------------------------------------------------------------------------

WRITER_MODEL = "claude-haiku-4-5-20251001"
WRITER_MAX_TOKENS = 2100

WRITER_SYSTEM_PROMPT = """\
You are a newsletter writer producing a daily briefing for a 23-year-old Swedish
university student studying Industrial Engineering and Management with strong interests in AI, ML, Data Science, quantitative finance, math and tech entrepreneurship.

Write in a clear, intelligent, slightly conversational tone. Not overly formal,
not casual. The reader is technically literate and intellectually curious.

Format the newsletter as valid HTML using inline styles only (for email compatibility).
Structure:
- Header with date and title "Morning Brief"
- One section per topic, each with a <h2> heading
- Each section: 1–2 tight paragraphs, 2–3 sentences each. Lead every paragraph with
  the concrete fact (what happened, what number, who) — do not open with scene-setting
  or throat-clearing. Cut connective filler ("it's worth noting", "in other news",
  "furthermore"). Only add context or explain significance if it's not obvious from
  the fact itself; never restate the fact in different words.
- End each section with a "Further reading" list of source links
- Brief closing line at the bottom

Total reading time: 4–6 minutes. Every sentence should carry a fact, a number, or a
concrete implication — no filler, no padding, no hedge words.

Some sections will be marked NO_NEW_DEVELOPMENTS — that topic had nothing new since
the last update (already-covered stories were filtered out upstream). For those,
write one short honest sentence saying there's nothing significant to report today.
Do not pad, invent stories, or restate old news to fill space. Skip the "Further
reading" list for that section.

HTML guidelines:
- Outer wrapper: <div style="max-width:600px;margin:0 auto;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Helvetica,Arial,sans-serif;background:#ffffff;color:#1a1a1a;padding:24px;">
- Title <h1>: font-size:28px;font-weight:700;margin-bottom:4px;color:#0f0f0f;
- Date line <p>: font-size:13px;color:#666;margin-top:0;margin-bottom:32px;
- Section <h2>: font-size:19px;font-weight:600;color:#0f0f0f;border-bottom:1px solid #e5e5e5;padding-bottom:6px;margin-top:32px;
- Body <p>: font-size:15px;line-height:1.65;color:#333;margin:12px 0;
- Further reading header <p>: font-size:13px;font-weight:600;color:#555;margin-top:16px;margin-bottom:4px;
- Further reading links <a>: color:#0066cc;text-decoration:none;font-size:13px;
- Closing line <p>: font-size:13px;color:#888;text-align:center;margin-top:40px;border-top:1px solid #e5e5e5;padding-top:16px;
"""
