"""
Sentiment analysis service for financial news articles.
Extracts sentiment and confidence scores using the local LLM.
"""

import json
from typing import Dict, Any, Tuple

from services.llm_service import LLMService
from config import SENTIMENT_OPTIONS, CONFIDENCE_THRESHOLD
from utils.logger import logger

class SentimentService:
    """Service for analyzing sentiment in financial news articles."""
    
    def __init__(self, llm_service: LLMService):
        """
        Initialize the sentiment service.
        
        Args:
            llm_service (LLMService): LLM service for text generation
        """
        self.llm_service = llm_service
    
    def analyze_sentiment(self, article: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze the sentiment of a financial news article.
        
        Args:
            article (Dict[str, Any]): Article data with headline and content
            
        Returns:
            Dict[str, Any]: Dictionary with sentiment and confidence score
        """
        headline = article.get("headline", "")
        content = article.get("content", "")
        
        # Create a prompt for sentiment analysis
        system_prompt = """
        You are a financial analyst expert at determining market sentiment from news articles.
        Analyze the given article for its potential impact on the stock market or on specific companies.
        You must classify the sentiment as one of: "positive", "neutral", or "negative".
        Also provide a confidence score from 0.0 to 1.0, where:
        - 0.0-0.3 means low confidence in your assessment
        - 0.4-0.7 means moderate confidence
        - 0.8-1.0 means high confidence
        
        Return ONLY a JSON object with two fields:
        - "sentiment": "positive", "neutral", or "negative"
        - "confidence": a float between 0.0 and 1.0
        
        For example: {"sentiment": "positive", "confidence": 0.85}
        """
        
        user_prompt = f"""
        Headline: {headline}
        
        Content: {content}
        
        Analyze the sentiment of this financial news and return only the JSON with sentiment and confidence.
        """
        
        try:
            # Use a cooler temperature for more consistent results
            result = self.llm_service.generate_completion(
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                temperature=0.1
            )
            
            # Parse the JSON response
            # The LLM might include extra text, so we need to extract the JSON
            json_pattern = result.strip()
            if not json_pattern.startswith("{"):
                # Find the first occurrence of a JSON-like pattern
                import re
                json_match = re.search(r'\{.*\}', result, re.DOTALL)
                if json_match:
                    json_pattern = json_match.group(0)
            
            sentiment_data = json.loads(json_pattern)
            
            # Validate the sentiment
            if "sentiment" not in sentiment_data or sentiment_data["sentiment"].lower() not in SENTIMENT_OPTIONS:
                logger.warning(f"Invalid sentiment value: {sentiment_data.get('sentiment')}. Defaulting to 'neutral'.")
                sentiment_data["sentiment"] = "neutral"
            
            # Validate the confidence
            if "confidence" not in sentiment_data or not isinstance(sentiment_data["confidence"], (int, float)):
                logger.warning("Invalid confidence value. Defaulting to 0.5.")
                sentiment_data["confidence"] = 0.5
            else:
                # Ensure confidence is between 0 and 1
                sentiment_data["confidence"] = max(0.0, min(1.0, float(sentiment_data["confidence"])))
            
            return sentiment_data
            
        except Exception as e:
            logger.error(f"Error analyzing sentiment: {str(e)}")
            # Return default values if analysis fails
            return {"sentiment": "neutral", "confidence": 0.5}