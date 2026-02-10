import os

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError("DATABASE_URL is not set in environment variables")

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
UPLOAD_DIR = "uploads"
CONFIDENCE_THRESHOLD = 0.85
