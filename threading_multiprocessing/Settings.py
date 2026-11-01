import os
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")


DESTINATION_FILE = os.getenv("DESTINATION_FILE")

AMAZON_DATES_FILE = os.getenv("AMAZON_DATES")
BITCOIN_DATES_FILE = os.getenv("BITCOIN_DATES")
GOOGLE_DATES_FILE = os.getenv("GOOGLE_DATES")

MAX_WORKERS = int(os.getenv("MAX_WORKERS"))

STOCKS = [
    ("Amazon", "AMZN", AMAZON_DATES_FILE),
    ("Bitcoin", "BTC-USD", BITCOIN_DATES_FILE),
    ("Google", "GOOGL", GOOGLE_DATES_FILE),
]
