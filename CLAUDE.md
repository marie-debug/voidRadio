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
  db.py                # SQLite schema + queries
  reddit_client.py     # PRAW wrapper
  fetcher.py           # Fetch job — pulls new posts from Reddit
```

## Development Guidelines

- MVP-first: get data flowing before optimizing
- Reddit sources: r/nosleep, r/creepypasta (expand later to SCP wiki, other sources)
- Store raw content alongside structured/tagged data — never discard the original
- Transmissions should feel like fragmented, in-universe radio intercepts
- Keep secrets (Reddit API credentials, Anthropic API key) in environment variables or a `.env` file, never committed

## Build / Run

```bash
uv sync
uv run main.py
```

## Tooling

- Always use `uv` for dependency management (`uv add`, `uv sync`, `uv run` — no pip)

## Current Status

Project bootstrapping — file structure and initial ingestion layer are first priorities.
