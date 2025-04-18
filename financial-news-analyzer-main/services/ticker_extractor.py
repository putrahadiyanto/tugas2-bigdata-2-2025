import json
import re
from typing import Dict, Any, List

from services.llm_service import LLMService
from utils.logger import logger

class TickerExtractorService:
    def __init__(self, llm_service: LLMService):
        self.llm_service = llm_service
    
    def extract_tickers(self, article: Dict[str, Any]) -> Dict[str, Any]:
        headline = article.get("headline", "")
        content = article.get("content", "")
        
        # Create a prompt for ticker extraction
        system_prompt = """
        You are a financial analyst specializing in identifying companies and their stock tickers mentioned in news articles.
        Your task is to identify stock tickers that are explicitly mentioned or strongly implied in the given article.
        For each identified ticker:
        1. Provide the standard stock ticker symbol (e.g., AAPL for Apple)
        2. Provide brief reasoning for why this ticker is relevant to the article
        
        Return ONLY a JSON object with:
        - "tickers": a list of strings with stock ticker symbols (e.g., ["AAPL", "MSFT", "GOOGL"])
        - "reasoning": string explaining why these tickers are relevant to the article
        
        For example:
        {
            "tickers": ["AAPL", "MSFT"],
            "reasoning": "Apple (AAPL) is the main subject of the article discussing their new product launch. Microsoft (MSFT) is mentioned as a competitor in the same market segment."
        }
        
        If no relevant tickers are found, return an empty list for tickers and explain why in the reasoning.
        """
        
        user_prompt = f"""
        Headline: {headline}
        
        Content: {content}
        
        Extract relevant stock tickers from this financial news article and provide reasoning for your choices.
        Return only the JSON with tickers and reasoning.
        """
        
        try:
            # Use a slightly higher temperature to allow for creative inference
            result = self.llm_service.generate_completion(
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                temperature=0.3
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
            
            ticker_data = json.loads(json_pattern)
            
            # Validate the tickers
            if "tickers" not in ticker_data or not isinstance(ticker_data["tickers"], list):
                logger.warning("Invalid tickers value. Defaulting to empty list.")
                ticker_data["tickers"] = []
            
            # Standardize ticker format (uppercase, no spaces)
            ticker_data["tickers"] = [self._standardize_ticker(ticker) for ticker in ticker_data["tickers"]]
            
            # Validate the reasoning
            if "reasoning" not in ticker_data or not isinstance(ticker_data["reasoning"], str):
                logger.warning("Invalid reasoning. Defaulting to empty string.")
                ticker_data["reasoning"] = ""
            
            return ticker_data
            
        except Exception as e:
            logger.error(f"Error extracting tickers: {str(e)}")
            # Return default values if extraction fails
            return {"tickers": [], "reasoning": "Error in ticker extraction process."}
    
    def _standardize_ticker(self, ticker: str) -> str:
        # Remove any non-alphanumeric characters except period (for BRK.A format)
        ticker = re.sub(r'[^A-Za-z0-9.]', '', ticker)
        return ticker.upper().strip()