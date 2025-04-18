import os
import multiprocessing
from pathlib import Path

# Project paths
BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
OUTPUT_DIR = BASE_DIR / "output"

# Ensure output directory exists    
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Data file paths
DATA_FILE = DATA_DIR / "news.json"
OUTPUT_FILE = OUTPUT_DIR / "analysis.json"

# LM Studio API configuration
LM_STUDIO_API_URL = "http://localhost:1234/v1/chat/completions"
LM_STUDIO_API_HEADERS = {
    "Content-Type": "application/json"
}

# LLM configuration
MAX_TOKENS = 1024
TEMPERATURE = 0.1  # Lower temperature for more deterministic responses

# Logging configuration
LOG_LEVEL = "INFO"
LOG_FORMAT = "%(asctime)s - %(levelname)s - %(message)s"

# Sentiment analysis configuration
SENTIMENT_OPTIONS = ["positive", "neutral", "negative"]
CONFIDENCE_THRESHOLD = 0.7  # Minimum confidence level to trust the analysis

# Multiprocessing configuration
MAX_WORKERS = max(1, min(3, multiprocessing.cpu_count() - 1))  # Limit to 3 workers max to avoid API overload

# Content truncation configuration
MAX_CONTENT_LENGTH = 8000  # Maximum characters for article content
MAX_HEADLINE_LENGTH = 200  # Maximum characters for article headline
PRESERVE_START_CHARS = 4000  # Characters to preserve from the beginning
PRESERVE_END_CHARS = 4000  # Characters to preserve from the end

# API Rate Limiting
MAX_CONCURRENT_REQUESTS = 2  # Maximum concurrent requests to LM Studio API
REQUEST_TIMEOUT = 90  # Timeout for API requests in seconds
MAX_RETRIES = 3  # Maximum number of retries for failed requests
RETRY_BACKOFF = 2  # Exponential backoff factor for retries
RETRY_DELAY = 3  # Initial delay between retries in seconds