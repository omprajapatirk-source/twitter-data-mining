import sys
from pathlib import Path

# Insert project root to sys.path
ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from server import app

# WSGI application callable for Vercel
app = app
