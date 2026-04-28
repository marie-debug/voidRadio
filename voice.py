import os
import re
import logging
from pathlib import Path
from dotenv import load_dotenv
from elevenlabs import ElevenLabs
from db import get_transmissions

load_dotenv()

logger = logging.getLogger("voidRadio.voice")

DEFAULT_MODEL = "eleven_turbo_v2_5"
OUTPUT_FORMAT = "mp3_44100_128"
AUDIO_DIR = Path("audio")

SPEAKER_TAG = re.compile(r"^\s*\[(PRESENTER|CALLER)\]\s*$")
SFX_TAG = re.compile(r"\[[A-Z][A-Z ]*\]")


def parse_segments(transmission_text):
    """Split transmission into ordered (speaker, text) segments.

    Lines tagged [PRESENTER]/[CALLER] set the active speaker. SFX tags like
    [STATIC] or [LINE DROPS] are stripped. Anything before the first speaker
    tag is dropped.
    """
    speaker = None
    buffers = []
    current = []

    def flush():
        if speaker and current:
            text = " ".join(current).strip()
            if text:
                buffers.append((speaker, text))

    for raw_line in transmission_text.splitlines():
        m = SPEAKER_TAG.match(raw_line)
        if m:
            flush()
            speaker = m.group(1)
            current = []
            continue
        cleaned = SFX_TAG.sub("", raw_line).strip()
        if cleaned:
            current.append(cleaned)

    flush()
    return buffers


def _voice_id_for(speaker):
    if speaker == "PRESENTER":
        return os.environ.get("ELEVENLABS_PRESENTER_VOICE_ID")
    return os.environ.get("ELEVENLABS_CALLER_VOICE_ID")


def synthesize_transmission(transmission, model=None):
    """Render a single transmission row to mp3. Returns the Path, or None if
    skipped (cached or empty parse)."""
    model = model or DEFAULT_MODEL
    AUDIO_DIR.mkdir(exist_ok=True)
    out_path = AUDIO_DIR / f"transmission_{transmission['id']}.mp3"

    if out_path.exists() and out_path.stat().st_size > 0:
        logger.info(f"  skip (cached): {out_path.name}")
        return out_path

    segments = parse_segments(transmission["transmission"])
    if not segments:
        logger.warning(f"  no speaker segments in transmission {transmission['id']} — skipping")
        return None

    client = ElevenLabs(api_key=os.environ["ELEVENLABS_API_KEY"])
    chunks = []
    for speaker, text in segments:
        voice_id = _voice_id_for(speaker)
        if not voice_id:
            raise RuntimeError(f"missing ELEVENLABS_{speaker}_VOICE_ID in env")
        audio = client.text_to_speech.convert(
            voice_id=voice_id,
            model_id=model,
            output_format=OUTPUT_FORMAT,
            text=text,
        )
        chunks.append(b"".join(audio))

    out_path.write_bytes(b"".join(chunks))
    logger.info(f"  rendered: {out_path.name} ({len(segments)} segments)")
    return out_path


def synthesize_all(limit=None, model=None):
    api_key = os.environ.get("ELEVENLABS_API_KEY")
    if not api_key:
        logger.warning("ELEVENLABS_API_KEY not set — skipping synthesis")
        return 0

    transmissions = get_transmissions(limit=limit)
    if not transmissions:
        logger.info("No transmissions to synthesize")
        return 0

    logger.info(f"Synthesizing {len(transmissions)} transmissions...")
    count = 0
    for t in transmissions:
        try:
            result = synthesize_transmission(t, model=model)
            if result is not None:
                count += 1
        except Exception as e:
            logger.error(f"  failed to synthesize transmission {t['id']}: {e}")

    return count


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )
    rendered = synthesize_all()
    logger.info(f"Done. {rendered} transmission(s) processed.")
