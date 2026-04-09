import logging
from datetime import datetime, timezone, timedelta
from db import init_db, get_stories, get_last_fetch_time
from fetcher import fetch_stories

FETCH_INTERVAL_DAYS = 4

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("voidRadio")


def main():
    logger.info("Initializing database...")
    init_db()

    last_fetch = get_last_fetch_time()
    now = datetime.now(timezone.utc)

    if last_fetch and (now - last_fetch) < timedelta(days=FETCH_INTERVAL_DAYS):
        days_left = FETCH_INTERVAL_DAYS - (now - last_fetch).days
        logger.info(f"Last fetch was {last_fetch.strftime('%Y-%m-%d %H:%M')} UTC — next fetch in ~{days_left} day(s), skipping")
    else:
        logger.info("Fetching stories from Reddit...")
        new_count = fetch_stories()
        logger.info(f"Ingested {new_count} new stories")

    stories = get_stories()
    logger.info(f"Total stories in database: {len(stories)}")

    if stories:
        logger.info("Recent stories:")
        for s in stories[:5]:
            logger.info(f"  [{s['subreddit']}] {s['title'][:80]} (score: {s['score']})")


if __name__ == "__main__":
    main()
