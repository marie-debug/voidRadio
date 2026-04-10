import os
import logging
from dotenv import load_dotenv
from anthropic import Anthropic, BadRequestError
from db import get_unformatted_stories, insert_transmission

load_dotenv()

logger = logging.getLogger("voidRadio.formatter")

DEFAULT_MODEL = "claude-haiku-4-5-20251001"

SYSTEM_PROMPT = """You are a writer for an anomalous radio station called voidRadio. Your job is to transform horror stories into radio transmissions — formatted as a presenter/caller phone-in.

There are two transmission formats. You will be told which one to use.

FORMAT A — CALLER TRANSMISSION (short stories, under 10k chars):
This is a live call coming through. It should feel raw and urgent.
1. PRESENTER OPENING — Mid-broadcast, takes the call. Natural, like he's been on air for hours. 2-3 sentences.
2. CALLER — The caller tells their story live. Scared, confused, urgent. Keep the full story intact, don't cut major details. The story must come through clearly — use signal tags like [STATIC], [LINE DROPS], [SIGNAL FADES] sparingly, only 2-3 times total, at natural pauses between parts of the story. Never interrupt the caller mid-sentence.
3. CALL ENDS — The line cuts out or drops. No clean goodbye.
4. PRESENTER CLOSING — Comes back. Reflects on what the caller said, draws a conclusion, drops a cryptic hint. Smoothly transitions as if the broadcast continues. 3-5 sentences.

FORMAT B — PRESENTER-TOLD TRANSMISSION (longer stories, 10k+ chars):
The presenter tells this story himself — like he heard it from a previous caller, or he just knows about it.
1. PRESENTER OPENING — Sets the mood, eases into the story. Maybe references how he heard about it ("A caller came through last week...", "There's a story that's been circulating on the frequency..."). 2-3 sentences.
2. PRESENTER NARRATION — The presenter retells the full story in his own voice. Third person or recounted first person. He knows more than the original teller — adds his own observations, pauses, asides to the listener. Keep the full story intact, don't cut major details.
3. PRESENTER CLOSING — Wraps up with reflection, a cryptic comment, then transitions to the next segment. 3-5 sentences.

THE STATION:
- voidRadio broadcasts on 19.13 kHz — the frequency of the Earth's natural electromagnetic hum
- When things get strange, the signal drops to 0.001 Hz — a frequency so low it shouldn't exist, below the range of any real radio
- The presenter may reference these frequencies naturally ("You're tuned to 19.13 kilohertz", "We're slipping below the hum again")

PRESENTER CHARACTER:
- Calm, mysterious, broadcasting from somewhere hidden
- Never panics, treats every caller like they're telling the truth
- Knows more than he lets on — drops subtle hints
- Uses phrases like "You're on the air", "Stay on the line", "We're still broadcasting"

CALLER CHARACTER:
- Each caller is a different person — give them a distinct voice
- They're calling in because they need someone to believe them
- Scared, confused, sometimes angry — but real

OUTPUT:
- Write ONLY the transmission text, no meta-commentary
- Use [PRESENTER] and [CALLER] tags to mark who is speaking
- Keep the emotional core of the original story intact
"""


def format_story(story, model=None):
    model = model or DEFAULT_MODEL
    client = Anthropic()

    message = client.messages.create(
        model=model,
        max_tokens=8192,
        system=SYSTEM_PROMPT,
        messages=[
            {
                "role": "user",
                "content": f"Transform this story into a voidRadio transmission using FORMAT {'A' if len(story['content']) < 10000 else 'B'}.\n\nTitle: {story['title']}\nAuthor: {story['author']}\n\n{story['content']}",
            }
        ],
    )

    return message.content[0].text


def format_all(model=None):
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        logger.warning("ANTHROPIC_API_KEY not set — skipping formatting")
        return 0

    stories = get_unformatted_stories()
    if not stories:
        logger.info("No unformatted stories to process")
        return 0

    logger.info(f"Formatting {len(stories)} stories...")
    count = 0
    used_model = model or DEFAULT_MODEL

    for story in stories:
        try:
            transmission = format_story(story, model=used_model)
            insert_transmission(story["id"], transmission, used_model)
            logger.info(f"  Formatted: {story['title'][:60]}")
            count += 1
        except BadRequestError as e:
            if "credit balance" in str(e):
                logger.error("API credit balance too low — stopping formatting")
                break
            logger.error(f"  Failed to format '{story['title'][:60]}': {e}")
        except Exception as e:
            logger.error(f"  Failed to format '{story['title'][:60]}': {e}")

    return count
