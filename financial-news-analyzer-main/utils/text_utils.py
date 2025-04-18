import re
from datetime import datetime
from typing import Optional, Dict, Any

from config import (
    MAX_CONTENT_LENGTH,
    MAX_HEADLINE_LENGTH,
    PRESERVE_START_CHARS,
    PRESERVE_END_CHARS
)

def parse_date(date_str: str) -> datetime:
    # Try different date formats
    formats = [
        "%Y-%m-%dT%H:%M:%SZ",  # ISO format with Z
        "%Y-%m-%dT%H:%M:%S.%fZ",  # ISO format with milliseconds and Z
        "%Y-%m-%d %H:%M:%S",  # Common datetime format
        "%Y-%m-%d",  # Just date
        "%b %d, %Y",  # Month name, day, year
        "%d %b %Y"  # Day, month name, year
    ]
    
    for fmt in formats:
        try:
            return datetime.strptime(date_str, fmt)
        except ValueError:
            continue
            
    # If no format matches, try to extract date using regex
    # This is a fallback mechanism
    date_pattern = r'(\d{4}[-/]\d{1,2}[-/]\d{1,2})'
    match = re.search(date_pattern, date_str)
    if match:
        try:
            return datetime.strptime(match.group(1), "%Y-%m-%d")
        except ValueError:
            try:
                return datetime.strptime(match.group(1), "%Y/%m/%d")
            except ValueError:
                pass
    
    # Return current date if all parsing attempts fail
    return datetime.now()

def normalize_text(text: str) -> str:
    # Replace multiple whitespace with single space
    text = re.sub(r'\s+', ' ', text)
    
    # Normalize quotes
    text = text.replace('"', '"').replace('"', '"')
    text = text.replace("'", "'").replace("'", "'")
    
    # Remove HTML tags if present
    text = re.sub(r'<[^>]+>', '', text)
    
    return text.strip()

def extract_effective_date(article: Dict[Any, Any]) -> datetime:
    if "published_at" in article and article["published_at"]:
        return parse_date(article["published_at"])
    
    # Try to find date in content as fallback
    if "content" in article and article["content"]:
        date_patterns = [
            r'(\d{1,2}\s+(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{4})',
            r'((?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},?\s+\d{4})',
            r'(\d{4}-\d{2}-\d{2})',
        ]
        
        for pattern in date_patterns:
            match = re.search(pattern, article["content"])
            if match:
                try:
                    return parse_date(match.group(1))
                except ValueError:
                    continue
    
    # Default to today if no date found
    return datetime.now()

def truncate_text(text: str, max_length: int, preserve_start: int, preserve_end: int) -> str:
    if not text or len(text) <= max_length:
        return text
    
    # If text is longer than max_length, truncate the middle
    if preserve_start + preserve_end >= max_length:
        # If the requested preserved parts would exceed max_length,
        # adjust to preserve more from the beginning (which typically has more important info)
        preserve_end = max(0, max_length - preserve_start)
    
    start_part = text[:preserve_start]
    end_part = text[-preserve_end:] if preserve_end > 0 else ""
    
    # Add ellipsis to indicate truncation
    truncated_text = f"{start_part}... [CONTENT TRUNCATED] ...{end_part}"
    
    return truncated_text