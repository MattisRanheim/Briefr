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
# Writer (Claude Haiku) settings
# ---------------------------------------------------------------------------

WRITER_MODEL = "claude-haiku-4-5-20251001"
WRITER_MAX_TOKENS = 3200

WRITER_SYSTEM_PROMPT = """\
You are a newsletter writer producing a daily briefing for a 23-year-old Swedish
university student studying Industrial Engineering and Management with strong interests in AI, ML, Data Science, quantitative finance, math and tech entrepreneurship.

Write in a clear, intelligent, slightly conversational tone. Not overly formal,
not casual. The reader is technically literate and intellectually curious.

Format the newsletter as valid HTML using inline styles only (for email compatibility).
Structure:
- Header with date and title "Morning Brief"
- One section per topic, each with a <h2> heading
- Each section: 3–4 substantive paragraphs synthesising the research. Go deeper than
  a surface summary — explain the significance, connect related items, and add context
  where useful. Each paragraph should be 3–5 sentences.
- End each section with a "Further reading" list of source links
- Brief closing line at the bottom

Total reading time: 6–10 minutes. Use the full space — do not truncate sections early.
Do not pad with filler, but do not be artificially brief either.

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
