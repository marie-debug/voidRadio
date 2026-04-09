# voidRadio

An anomalous radio station powered by collaborative fiction scraped from the internet.

voidRadio ingests SCP-style and horror fiction from Reddit (r/nosleep, r/creepypasta, etc.), structures it into a living dataset, and continuously broadcasts ambient transmissions as if they're coming from inside the universe.

## Architecture

```
voidRadio/
  main.py              # Entry point
  db.py                # SQLite schema + queries
  reddit_client.py     # PRAW wrapper
  fetcher.py           # Job that pulls new posts
```

## Core Components

1. **Ingestion layer** — PRAW (Reddit API wrapper) to pull posts from r/nosleep, r/creepypasta, etc. with metadata (score, flair, date, author)
2. **Storage** — SQLite, storing raw content + structured fields
3. **Processing layer** — Extract entities, themes, and "anomaly type" tags using Claude API or spaCy
4. **Broadcast engine** — A scheduler that selects content and emits it as formatted "transmissions"

## MVP Sequence

1. Reddit ingest → SQLite (raw stories stored)
2. Simple tagging (keyword-based or LLM) to classify anomaly type
3. Formatter that rewrites excerpts as fragmented radio transmissions
4. Broadcast loop that plays/prints them with ambient timing

## Key Libraries

- `praw` — Reddit API
- `sqlite3` — Storage
- `anthropic` — Claude API for formatting/tagging
- `pyttsx3` / `gTTS` — TTS for audio output
- `apscheduler` — Broadcast scheduling

## Setup

```bash
uv sync
uv run main.py
```

You'll need a Reddit API app configured — see [PRAW docs](https://praw.readthedocs.io/en/stable/getting_started/quick_start.html).

## License

TBD
