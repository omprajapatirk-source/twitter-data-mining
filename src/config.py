import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env file from project root
BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

# Twitter API Credentials
TWITTER_BEARER_TOKEN = os.getenv("TWITTER_BEARER_TOKEN", "")
TWITTER_API_KEY = os.getenv("TWITTER_API_KEY", "")
TWITTER_API_SECRET = os.getenv("TWITTER_API_SECRET", "")
TWITTER_ACCESS_TOKEN = os.getenv("TWITTER_ACCESS_TOKEN", "")
TWITTER_ACCESS_TOKEN_SECRET = os.getenv("TWITTER_ACCESS_TOKEN_SECRET", "")

import tempfile

# Data Paths
try:
    DATA_DIR = BASE_DIR / "data"
    DATA_DIR.mkdir(exist_ok=True)
    DEFAULT_STREAM_FILE = DATA_DIR / "stream_data.jsonl"
except (OSError, PermissionError):
    DATA_DIR = Path(tempfile.gettempdir()) / "twitter_data"
    DATA_DIR.mkdir(exist_ok=True)
    DEFAULT_STREAM_FILE = DATA_DIR / "stream_data.jsonl"

# Server Port
PORT = int(os.getenv("PORT", 5000))
DEBUG = os.getenv("DEBUG", "False").lower() in ("true", "1", "yes")
