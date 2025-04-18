import json
import requests
import time
import threading
from typing import List, Dict, Any, Optional
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from queue import Queue, Empty
import concurrent.futures

from config import (
    LM_STUDIO_API_URL, 
    LM_STUDIO_API_HEADERS, 
    MAX_TOKENS,
    TEMPERATURE,
    MAX_CONCURRENT_REQUESTS,
    REQUEST_TIMEOUT,
    MAX_RETRIES,
    RETRY_BACKOFF,
    RETRY_DELAY
)
from utils.logger import logger

class APIRateLimiter:
    def __init__(self, max_concurrent_requests: int):
        self.semaphore = threading.Semaphore(max_concurrent_requests)
        self.active_requests = 0
        self.lock = threading.Lock()
    
    def __enter__(self):
        """Acquire the semaphore (wait if too many active requests)."""
        self.semaphore.acquire()
        with self.lock:
            self.active_requests += 1
            logger.debug(f"Active API requests: {self.active_requests}")
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Release the semaphore when request is complete."""
        with self.lock:
            self.active_requests -= 1
            logger.debug(f"Active API requests: {self.active_requests}")
        self.semaphore.release()

class LLMService:
    """Base service for interacting with the local LLM via HTTP API."""
    
    def __init__(self):
        self.api_url = LM_STUDIO_API_URL
        self.headers = LM_STUDIO_API_HEADERS
        self.max_tokens = MAX_TOKENS
        self.temperature = TEMPERATURE
        self.rate_limiter = APIRateLimiter(MAX_CONCURRENT_REQUESTS)
        
        # Create a session with retry capability
        self.session = requests.Session()
        retry_strategy = Retry(
            total=MAX_RETRIES,
            backoff_factor=RETRY_BACKOFF,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["POST"]
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)
    
    def generate_completion(
        self, 
        system_prompt: str, 
        user_prompt: str,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None
    ) -> str:
        if temperature is None:
            temperature = self.temperature
        
        if max_tokens is None:
            max_tokens = self.max_tokens
        
        payload = {
            "model": "local-model",  # LM Studio uses this identifier for the local model
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            "temperature": temperature,
            "max_tokens": max_tokens
        }
        
        # Use rate limiter to limit concurrent requests
        with self.rate_limiter:
            try:
                retry_count = 0
                while retry_count <= MAX_RETRIES:
                    try:
                        logger.info("Sending request to LLM API")
                        response = self.session.post(
                            self.api_url,
                            headers=self.headers,
                            json=payload,
                            timeout=REQUEST_TIMEOUT
                        )
                        
                        response.raise_for_status()
                        result = response.json()
                        
                        # Extract the content from the response
                        if "choices" in result and len(result["choices"]) > 0:
                            return result["choices"][0]["message"]["content"]
                        else:
                            logger.error(f"Unexpected API response structure: {result}")
                            raise ValueError("Unexpected API response structure")
                    
                    except (requests.exceptions.RequestException, ValueError) as e:
                        retry_count += 1
                        if retry_count > MAX_RETRIES:
                            logger.error(f"API request failed after {MAX_RETRIES} retries: {str(e)}")
                            raise
                        
                        # Calculate exponential backoff delay
                        delay = RETRY_DELAY * (RETRY_BACKOFF ** (retry_count - 1))
                        logger.warning(f"API request failed, retrying in {delay:.1f} seconds (attempt {retry_count}/{MAX_RETRIES}): {str(e)}")
                        time.sleep(delay)
                
                # This should not be reached due to the raise in the loop
                raise Exception("Unexpected code flow in API request retry loop")
                    
            except requests.exceptions.RequestException as e:
                logger.error(f"API request failed: {str(e)}")
                raise Exception(f"Failed to get response from LLM API: {str(e)}")
            except (KeyError, IndexError, json.JSONDecodeError) as e:
                logger.error(f"Error processing API response: {str(e)}")
                raise Exception(f"Error processing API response: {str(e)}")
                
    def shutdown(self):
        """Clean up resources when the service is no longer needed."""
        self.session.close()