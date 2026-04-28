# CLAUDE.md — voidRadio

## Project Overview

voidRadio is an experimental "anomalous radio station" — a continuous broadcast system that ingests horror/SCP-style collaborative fiction from Reddit, processes it, and emits ambient transmissions as if they're coming from inside the fiction universe.

## Tech Stack

- **Language:** Python
- **Reddit API:** PRAW
- **Storage:** SQLite
- **LLM:** Anthropic Claude API for content tagging and transmission formatting
- **TTS:** ElevenLabs (distinct voices for presenter vs caller)
- **Scheduling:** apscheduler

## Project Structure

```
voidRadio/
  main.py              # Entry point
  db.py                # SQLite schema + queries (stories + transmissions tables)
  reddit_client.py     # PRAW wrapper
  fetcher.py           # Fetch job — pulls top-rated posts from Reddit
  formatter.py         # Claude API — transforms stories into radio transmissions
  voice.py             # ElevenLabs TTS — synthesizes transmissions to audio/*.mp3
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

### Broadcast Engine (next up)
- Build `scheduler.py` — continuous broadcast loop that selects and plays transmissions with ambient timing
- For MVP, iterate over `audio/*.mp3` directly; DB metadata routing can come later
- **Test fixtures:** use the 2 existing MP3s in `audio/` (`transmission_53.mp3` Format A with caller, `transmission_58.mp3` Format B presenter-only) — **don't re-run `main.py` / `voice.py` while developing `scheduler.py`**. No need to re-fetch from Reddit, re-format with Claude, or re-synthesize with ElevenLabs. The 2 MP3s are enough to prototype playback, ordering, and ambient timing
- **Backup copies** of the 2 fixture MP3s live at `/home/marion/Desktop/void radio audio/` in case `audio/` gets cleared (it's gitignored)
- The remaining ~25 transmissions will be synthesized in a later batch once the broadcast engine is solid

### Voices
- Currently using **free default ElevenLabs voices** for presenter and caller — good enough to validate the pipeline
- Later: create custom/distinct voices that match the station identity (calm/mysterious presenter, scared/urgent callers). Likely via ElevenLabs voice cloning or designed voices
- Also later: rotate multiple caller voices instead of one shared caller voice

### Wire `voice.py` into `main.py`
- Currently standalone (`uv run voice.py`) — wire into the fetch → format → synthesize pipeline once cost/quality is comfortable
- Consider real audio SFX mixing for `[STATIC]` / `[LINE DROPS]` (currently stripped)

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

### 2026-04-28
- Built `voice.py` — ElevenLabs TTS: parses `[PRESENTER]`/`[CALLER]` tags, strips SFX tags (e.g. `[STATIC]`, `[LINE DROPS]`) for MVP, synthesizes each segment with the matching voice, concatenates MP3 chunks per transmission to `audio/transmission_{id}.mp3`. Caches by file existence so we never pay twice for the same audio
- Added `elevenlabs` dependency
- Added `ELEVENLABS_PRESENTER_VOICE_ID` and `ELEVENLABS_CALLER_VOICE_ID` env vars (per-speaker voice routing without code changes)
- Added `audio/` to `.gitignore`
- Smoke-tested on two transmissions (one Format B presenter-only, one Format A with caller) — voices distinct, no SFX tag words spoken, no jarring seams from byte-level MP3 concat
- **MVP scope:** keeping just these 2 MP3s as the working set for now (enough to prototype `scheduler.py` against); the remaining ~25 transmissions will be synthesized later
- **MVP scope:** using free default ElevenLabs voices for now; custom/distinct voices that match the station identity (calm presenter / scared callers) come later
