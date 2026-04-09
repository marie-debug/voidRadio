import logging
from reddit_client import get_reddit_client
from db import story_exists, insert_story

logger = logging.getLogger(__name__)

DEFAULT_SUBREDDITS = ["nosleep", "creepypasta"]


def fetch_stories(subreddits=None, limit=25, sort="hot"):
    subreddits = subreddits or DEFAULT_SUBREDDITS
    reddit = get_reddit_client()
    total_new = 0

    for sub_name in subreddits:
        logger.info(f"Fetching from r/{sub_name} ({sort}, limit={limit})")
        subreddit = reddit.subreddit(sub_name)

        if sort == "hot":
            posts = subreddit.hot(limit=limit)
        elif sort == "new":
            posts = subreddit.new(limit=limit)
        elif sort == "top":
            posts = subreddit.top(limit=limit, time_filter="week")
        else:
            posts = subreddit.hot(limit=limit)

        new_count = 0
        for post in posts:
            if not post.is_self or not post.selftext:
                continue
            if story_exists(post.id):
                continue

            insert_story({
                "reddit_id": post.id,
                "subreddit": sub_name,
                "title": post.title,
                "author": str(post.author) if post.author else "[deleted]",
                "content": post.selftext,
                "score": post.score,
                "flair": post.link_flair_text,
                "url": f"https://reddit.com{post.permalink}",
                "created_utc": post.created_utc,
            })
            new_count += 1

        logger.info(f"  r/{sub_name}: {new_count} new stories")
        total_new += new_count

    return total_new
