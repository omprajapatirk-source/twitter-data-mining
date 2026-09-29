"""
Realistic Twitter / X Stream Generator
Generates realistic JSONL tweet streams complete with user metadata, geo coordinates,
hashtags, mentions, metrics, and timestamps for testing and offline data mining.
"""

import json
import random
import tempfile
from datetime import datetime, timedelta, timezone
from pathlib import Path

LOCATIONS = [
    {"city": "San Francisco, USA", "lat": 37.7749, "lng": -122.4194},
    {"city": "New York, USA", "lat": 40.7128, "lng": -74.0060},
    {"city": "London, UK", "lat": 51.5074, "lng": -0.1278},
    {"city": "Tokyo, Japan", "lat": 35.6762, "lng": 139.6503},
    {"city": "Berlin, Germany", "lat": 52.5200, "lng": 13.4050},
    {"city": "Paris, France", "lat": 48.8566, "lng": 2.3522},
    {"city": "Bengaluru, India", "lat": 12.9716, "lng": 77.5946},
    {"city": "Toronto, Canada", "lat": 43.6532, "lng": -79.3832},
    {"city": "Sydney, Australia", "lat": -33.8688, "lng": 151.2093},
    {"city": "São Paulo, Brazil", "lat": -23.5505, "lng": -46.6333}
]

USERS = [
    {"username": "tech_guru", "name": "Alex Mercer", "verified": True},
    {"username": "data_ninja", "name": "Elena Rostova", "verified": False},
    {"username": "py_dev", "name": "Marco Bonzanini Fan", "verified": True},
    {"username": "ai_researcher", "name": "Dr. Sarah Chen", "verified": True},
    {"username": "cloud_native", "name": "Liam O'Connor", "verified": False},
    {"username": "sports_fanatic", "name": "Jordan Smith", "verified": False},
    {"username": "eco_warrior", "name": "Greta Green", "verified": False},
    {"username": "code_wizard", "name": "Devin Kumar", "verified": True}
]

TWEET_TEMPLATES = [
    # AI & ML
    ("Just tested the new open source LLM with #Python and #DataScience! The inference speed is incredible 🚀 @py_dev", "positive"),
    ("Exploring natural language processing with custom regex tokenizers. #AI #NLP is changing everything!", "positive"),
    ("Deep learning model keeps running out of memory during fine-tuning. Super frustrating bug 😡 #AI #MachineLearning", "negative"),
    ("Co-occurrence matrices and Pointwise Mutual Information (PMI) are classic text mining algorithms that still shine. #Python #DataScience", "positive"),
    ("Reviewing the latest research paper on multi-agent collaboration in #AI. Very promising concepts! #Tech", "positive"),
    
    # Software & Python
    ("Working on mining Twitter data with #Python and @tweepy! Love this classic workflow ❤️ #Coding", "positive"),
    ("The latest release broke backward compatibility for our production API. Terrible update 👎 #Software #Bug", "negative"),
    ("Building interactive dashboards with Flask and Chart.js. Clean, fast, and modern! #WebDev #Python", "positive"),
    ("Why is asynchronous I/O in Python so elegant? Check out the new benchmarks: https://github.com/example/async #Python #Dev", "neutral"),
    ("Anyone else experiencing outages with their cloud database provider today? Major headache. #Cloud #DevOps", "negative"),
    
    # Business & Startups
    ("Excited to announce our seed round funding to revolutionize automated data analytics! 🎉 @tech_guru #Startup #Tech", "positive"),
    ("Market volatility is at an all-time high this quarter. Staying cautious with tech stocks. #Business #Markets", "neutral"),
    ("Our product launch hit 10,000 active users in the first 48 hours! Massive thank you to everyone ❤️ #Startup #Milestone", "positive"),
    ("Customer churn rate spiked unexpectedly this month. Time to rethink the onboarding flow. #Business #SaaS", "negative"),
    
    # Science & Climate
    ("Fascinating new telemetry data received from deep space exploration! 🛰️ #NASA #Space #Science", "positive"),
    ("Global temperatures reached record highs last month. We urgently need renewable energy adoption 🌍 #ClimateChange #Earth", "negative"),
    ("New solar panel efficiency breakthrough announced by university labs! Clean energy is the future. #Science #CleanEnergy", "positive"),
    
    # Sports & Events
    ("What a thrilling comeback victory in tonight's championship match! Best game of the season! 🏆 #Sports #Winner", "positive"),
    ("Heartbreaking defeat for the home team in the final minutes. Utterly disappointed 😢 #Football #MatchDay", "negative"),
    ("Pre-game press conference is live now discussing tactical lineups. #Sports #News", "neutral")
]

# In-memory storage cache for serverless environments
MEMORY_TWEETS_CACHE = []

def generate_mock_tweets(count: int = 150) -> list[dict]:
    """Generates a list of realistic synthetic tweet dictionaries."""
    tweets = []
    base_time = datetime.now(timezone.utc) - timedelta(hours=48)

    for i in range(count):
        template, expected_sentiment = random.choice(TWEET_TEMPLATES)
        user = random.choice(USERS)
        loc = random.choice(LOCATIONS)
        
        tweet_time = base_time + timedelta(minutes=random.randint(5, 48 * 60))
        time_str = tweet_time.strftime("%Y-%m-%dT%H:%M:%SZ")

        retweets = random.randint(0, 450)
        likes = random.randint(retweets, retweets * 8 + 5)
        replies = random.randint(0, retweets // 2 + 3)

        tweet = {
            "id": str(1700000000000000000 + i + random.randint(1000, 99999)),
            "text": template,
            "created_at": time_str,
            "author_id": f"usr_{hash(user['username']) % 1000000}",
            "user": {
                "name": user["name"],
                "username": user["username"],
                "verified": user["verified"],
                "location": loc["city"],
                "followers_count": random.randint(300, 45000)
            },
            "geo": {
                "place_name": loc["city"],
                "coordinates": [loc["lat"], loc["lng"]]
            },
            "public_metrics": {
                "retweet_count": retweets,
                "like_count": likes,
                "reply_count": replies
            },
            "lang": "en"
        }
        tweets.append(tweet)

    tweets.sort(key=lambda t: t["created_at"])
    return tweets

def save_mock_dataset(filepath: str | Path, count: int = 150) -> list[dict]:
    """Generates and writes mock tweets to a JSONL file with memory/tempdir fallbacks."""
    global MEMORY_TWEETS_CACHE
    tweets = generate_mock_tweets(count)
    MEMORY_TWEETS_CACHE = tweets

    paths_to_try = [Path(filepath), Path(tempfile.gettempdir()) / "stream_data.jsonl"]
    
    for path in paths_to_try:
        try:
            path.parent.mkdir(parents=True, exist_ok=True)
            with open(path, "w", encoding="utf-8") as f:
                for tweet in tweets:
                    f.write(json.dumps(tweet, ensure_ascii=False) + "\n")
            break
        except (OSError, PermissionError):
            continue

    return tweets
