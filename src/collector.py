"""
Twitter / X Data Ingestion and Stream Collector
Based on Marco Bonzanini's Data Collection Architecture (Part 1)
Supports live Twitter API v2 (Tweepy), keyword searches, and automatic mock stream fallback.
"""

import json
import tempfile
from pathlib import Path
from typing import Optional
import tweepy

from .config import (
    TWITTER_BEARER_TOKEN,
    TWITTER_API_KEY,
    TWITTER_API_SECRET,
    TWITTER_ACCESS_TOKEN,
    TWITTER_ACCESS_TOKEN_SECRET,
    DEFAULT_STREAM_FILE
)
from .mock_generator import generate_mock_tweets, save_mock_dataset, MEMORY_TWEETS_CACHE

class TwitterCollector:
    """Handles data collection from Twitter API v2 or local simulated streams."""

    def __init__(self, bearer_token: Optional[str] = None):
        self.bearer_token = bearer_token or TWITTER_BEARER_TOKEN
        self.client = None
        if self.bearer_token:
            try:
                self.client = tweepy.Client(
                    bearer_token=self.bearer_token,
                    consumer_key=TWITTER_API_KEY or None,
                    consumer_secret=TWITTER_API_SECRET or None,
                    access_token=TWITTER_ACCESS_TOKEN or None,
                    access_token_secret=TWITTER_ACCESS_TOKEN_SECRET or None
                )
            except Exception as e:
                print(f"[Warning] Failed to initialize Tweepy Client: {e}")

    def collect_recent_tweets(
        self,
        query: str = "#python -is:retweet lang:en",
        max_results: int = 50,
        output_file: Optional[Path] = None
    ) -> list[dict]:
        """
        Fetches recent tweets using Twitter API v2 search endpoint.
        Falls back to generating realistic mock data if no valid API credentials are found.
        """
        target_path = Path(output_file or DEFAULT_STREAM_FILE)

        if self.client:
            try:
                print(f"[Collector] Querying Twitter API v2 with: '{query}'...")
                response = self.client.search_recent_tweets(
                    query=query,
                    max_results=min(max_results, 100),
                    tweet_fields=["created_at", "public_metrics", "lang", "geo", "entities"],
                    expansions=["author_id", "geo.place_id"],
                    user_fields=["username", "name", "location", "verified", "public_metrics"]
                )

                if response.data:
                    users_lookup = {}
                    if response.includes and "users" in response.includes:
                        for u in response.includes["users"]:
                            users_lookup[u.id] = {
                                "username": u.username,
                                "name": u.name,
                                "verified": getattr(u, "verified", False),
                                "location": getattr(u, "location", "Unknown")
                            }

                    collected = []
                    for tweet in response.data:
                        user_info = users_lookup.get(tweet.author_id, {
                            "username": "unknown",
                            "name": "Twitter User",
                            "verified": False,
                            "location": "Global"
                        })

                        tweet_dict = {
                            "id": str(tweet.id),
                            "text": tweet.text,
                            "created_at": tweet.created_at.isoformat() if tweet.created_at else "",
                            "author_id": str(tweet.author_id),
                            "user": user_info,
                            "public_metrics": tweet.public_metrics or {},
                            "lang": getattr(tweet, "lang", "en")
                        }
                        collected.append(tweet_dict)

                    # Try to save to file
                    try:
                        target_path.parent.mkdir(parents=True, exist_ok=True)
                        with open(target_path, "a", encoding="utf-8") as f:
                            for t in collected:
                                f.write(json.dumps(t, ensure_ascii=False) + "\n")
                    except (OSError, PermissionError):
                        pass

                    return collected

            except Exception as e:
                print(f"[Collector Error] Twitter API call failed: {e}")

        # Fallback to mock generator
        return save_mock_dataset(target_path, count=max_results)

    @staticmethod
    def load_tweets(filepath: Optional[Path] = None) -> list[dict]:
        """Loads and parses tweets from files or memory."""
        global MEMORY_TWEETS_CACHE
        paths_to_check = [
            Path(filepath) if filepath else None,
            DEFAULT_STREAM_FILE,
            Path(tempfile.gettempdir()) / "stream_data.jsonl"
        ]

        for p in paths_to_check:
            if p and p.exists():
                tweets = []
                try:
                    with open(p, "r", encoding="utf-8") as f:
                        for line in f:
                            line = line.strip()
                            if line:
                                tweets.append(json.loads(line))
                    if tweets:
                        return tweets
                except Exception:
                    continue

        if MEMORY_TWEETS_CACHE:
            return MEMORY_TWEETS_CACHE

        # Generate on the fly
        return save_mock_dataset(DEFAULT_STREAM_FILE, count=80)
