# NewsofAI

An Instagram workflow for Reels scripts, subtitles, carousel and Stories copy,
Gemini narration, original instrumental music, vertical videos, and publishing
selected final videos. Try the musical demo without an API key:
`python prepare_reel.py --demo` (requires FFmpeg).
See [INSTAGRAM.md](INSTAGRAM.md) for the full guide. Publishing requires an
Instagram connection, hosting for the final media, and an explicit `--publish` command.

The Telegram bot fetches AI news from RSS feeds, uses Gemini to summarize it in
natural Uzbek, and publishes it to a Telegram channel. Requires Python 3.12+;
the Telegram bot needs no additional Python packages.

## Getting started

1. Create a Telegram bot with @BotFather and add it to your channel as an
   administrator with permission to publish posts.
2. Set the environment variables `TELEGRAM_BOT_TOKEN`, `TELEGRAM_CHANNEL_ID`
   (`@channel_name` or a numeric ID for a private channel), and `GEMINI_API_KEY`.
   Never put keys in chat or Git. `.env.example` is only a template;
   the application does not load `.env` files automatically.
3. Run the tests from the repository directory:
   `python3 -m unittest discover -s tests -v`.
4. Preview the generated text with `python3 bot.py --dry-run`. This calls Gemini
   but does not send anything to the channel or mark the article as sent.
5. Run `python3 bot.py` to start the continuous worker. Use `--once` to run a
   single cycle.

`POST_INTERVAL_HOURS` defaults to 1.5 (90 minutes). The bot checks every five
minutes and waits at least the configured interval after the last post.
It does not publish when there is no news. It publishes **at most 18 posts per
Asia/Tashkent calendar day**, regardless of the interval setting.
The bot caches up to 14 days of RSS history, triages up to 80 leads across
age groups, then reviews up to three promising stories against a retrieved
primary source before posting one. Importance outranks recency; weak or
unverifiable stories are skipped. The default sources are TechCrunch and The Verge; set `FEED_URLS` to a comma-separated list of
RSS/Atom URLs to use other sources. `GEMINI_MODEL` defaults to `gemini-2.5-flash`.

SQLite state is stored in `.local/posts.sqlite3` (override with `STATE_PATH`).
Preserve this file across restarts and use one shared database per channel.
The same URL will not be posted again. A model-derived event key also suppresses coverage of the same event across
different URLs. Semantic deduplication is fallible; URL deduplication and
pending-send protection remain in place.

If a Telegram request returns no response, the article remains `pending` and
is not retried automatically. Check the channel before resolving it manually.
`pending` records also count toward the daily limit. AI-generated content may
contain errors; review test posts before starting the worker.

Required HTTPS destinations: `techcrunch.com`, `www.theverge.com`,
`generativelanguage.googleapis.com`, `api.telegram.org`, and the primary-source
hosts linked by selected articles. Source fetches require public HTTPS/DNS and
validate redirect destinations.
Live RSS retrieval, AI generation, and Telegram delivery must be verified
separately with network access and valid credentials.

## Telegram editorial review

See [TELEGRAM_EDITORIAL.md](TELEGRAM_EDITORIAL.md) for selection, evidence,
caching, audit records and deployment limitations. The existing Gemini key and
model are reused. Editorial review adds model requests; its 90-minute cooldown
also applies to empty/failed attempts to prevent five-minute paid retries.
