import logging
import os

DEBUG = os.getenv("DEBUG", False)

LOG_LEVEL = os.getenv("LOG_LEVEL", logging.ERROR)

SCRAPER_USER_AGENT = os.getenv(
    "SCRAPER_USER_AGENT", "Mozilla/5.0 (compatible; SafePlateBot/0.1)"
)

DATABASE_URI = os.getenv("DATABASE_URI", "mongodb://localhost:27017")
DATABASE_NAME = os.getenv("DATABASE_NAME", "safeplate")

WEBHOOK_API_KEY = os.getenv("WEBHOOK_API_KEY", "secret")
WEBHOOK_URL = os.getenv("WEBHOOK_URL", "http://localhost:44778/api/recipes")
