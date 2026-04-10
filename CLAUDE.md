# CLAUDE.md — voidRadio

## Project Overview

voidRadio is an experimental "anomalous radio station" — a continuous broadcast system that ingests horror/SCP-style collaborative fiction from Reddit, processes it, and emits ambient transmissions as if they're coming from inside the fiction universe.

## Tech Stack

- **Language:** Python
- **Reddit API:** PRAW
- **Storage:** SQLite
- **LLM:** Anthropic Claude API for content tagging and transmission formatting
- **TTS:** pyttsx3 or gTTS (optional audio output)
- **Scheduling:** apscheduler

## Project Structure

```
voidRadio/
  main.py              # Entry point
  db.py                # SQLite schema + queries (stories + transmissions tables)
  reddit_client.py     # PRAW wrapper
  fetcher.py           # Fetch job — pulls top-rated posts from Reddit
  formatter.py         # Claude API — transforms stories into radio transmissions
```

## Development Guidelines

- MVP-first: get data flowing before optimizing
- Reddit sources: r/nosleep, r/creepypasta (expand later to SCP wiki, other sources)
- Store raw content alongside structured/tagged data — never discard the original
- Transmissions should feel like a live radio broadcast — not scripted or rigid
- Keep secrets (Reddit API credentials, Anthropic API key) in environment variables or a `.env` file, never committed

## Build / Run

```bash
uv sync
uv run main.py
```

## Tooling

- Always use `uv` for dependency management (`uv add`, `uv sync`, `uv run` — no pip)

## Station Identity

- **Frequency:** 19.13 kHz (Earth's electromagnetic hum) — the station's "home" frequency
- **Secondary frequency:** 0.001 Hz — impossibly low, used when things get strange
- **Presenter:** calm, mysterious, knows more than he lets on, broadcasting from somewhere hidden. Never panics. Treats every caller like they're telling the truth
- **Callers:** scared, confused, urgent — calling in because they need someone to believe them

## Transmission Formats

- **Format A (Caller)** — stories under 10k chars. Live call feel, raw and urgent. Signal effects ([STATIC], [LINE DROPS]) used sparingly (2-3 max), never mid-sentence
- **Format B (Presenter-told)** — stories 10k+ chars. Presenter narrates in his own voice, like he heard it from a previous caller or just knows about it

## Data Quality

- Fetch sort: `top` (weekly)
- Minimum score: 10
- Creepypasta: only `Text Story` flair accepted
- Formatter uses Haiku for dev/testing, Sonnet for real output
- Transmissions stored in DB so we never pay twice for the same story

## Next Steps

### Audio (ElevenLabs)
- Build `voice.py` — pipe formatted transmissions through ElevenLabs API for spoken audio
- Distinct voices for presenter vs callers
- ElevenLabs API key already in `.env`

### Broadcast Engine
- Build `scheduler.py` — continuous broadcast loop that selects and plays transmissions with ambient timing

### Future: SCP Wiki Source
- Add SCP Wiki scraper as second content source (Creative Commons licensed, better long-term fit)
- Architecture is already source-agnostic — only a new fetcher needed

## Progress Log

### 2026-04-08
- Set up project with `uv init`, added praw and python-dotenv deps
- Built Reddit ingestion pipeline: `reddit_client.py` (PRAW wrapper), `fetcher.py` (pulls from r/nosleep, r/creepypasta)
- Built SQLite storage layer: `db.py` with stories table (reddit_id, title, author, content, score, flair, url, timestamps)
- Added 4-day fetch cooldown — checks last fetch time before hitting Reddit API
- Successfully ingested 33 stories on first run
- Initial commit pushed

### 2026-04-09
- Built `formatter.py` — Claude API transforms stories into radio transmissions (two formats: caller vs presenter-told)
- Added `transmissions` table to DB with story_id FK, model tracking, timestamps
- Added `anthropic` dependency

### 2026-04-10
- Data cleanup: filtered creepypasta to `Text Story` flair only, set minimum score threshold (10), switched fetch sort from `hot` to `top`
- Cleaned DB of low-quality/removed stories
- Defined station identity: 19.13 kHz primary frequency, 0.001 Hz secondary
- Successfully formatted 25 stories into transmissions using Haiku
