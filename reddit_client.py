import os
import praw
from dotenv import load_dotenv

load_dotenv()


def get_reddit_client():
    return praw.Reddit(
        client_id=os.environ["CLIENT_ID"],
        client_secret=os.environ["SECRET"],
        user_agent=os.environ.get("AGENT", "voidRadio/0.1"),
    )
