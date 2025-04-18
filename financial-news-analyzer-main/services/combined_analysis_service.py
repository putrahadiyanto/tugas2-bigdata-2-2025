import json
import re
import os
from typing import Dict, Any, List, Tuple

from services.llm_service import LLMService
from services.summarizer_service import SummarizerService
from config import SENTIMENT_OPTIONS, DATA_DIR
from utils.logger import logger


class CombinedAnalysisService:
    def __init__(self, llm_service: LLMService):
        self.llm_service = llm_service
        self.summarizer_service = SummarizerService(llm_service)
        self.ticker_company_map = self._load_ticker_company_map()
        self.valid_tickers = list(self.ticker_company_map.keys())
    
    def _load_ticker_company_map(self) -> Dict[str, str]:
        """
        Load ticker to company name mapping from ticker_company.json file.
        
        Returns:
            Dict[str, str]: Mapping of ticker symbols to company names
        """
        ticker_company_map = {}
        try:
            ticker_company_path = os.path.join(DATA_DIR, "ticker_company.json")
            with open(ticker_company_path, 'r', encoding='utf-8') as f:
                ticker_company_map = json.load(f)
            
            logger.info(f"Loaded {len(ticker_company_map)} ticker-company mappings from ticker_company.json")
                    
        except Exception as e:
            logger.error(f"Error loading ticker-company mapping: {str(e)}")
            # Fallback to some common IDX tickers if file can't be loaded
            ticker_company_map = {
                "BBCA": "Bank Central Asia Tbk.",
                "BBRI": "Bank Rakyat Indonesia Tbk.",
                "BMRI": "Bank Mandiri Tbk.",
                "TLKM": "Telkom Indonesia Tbk.",
                "UNVR": "Unilever Indonesia Tbk.",
                "ASII": "Astra International Tbk.",
                "HMSP": "H.M. Sampoerna Tbk.",
                "ICBP": "Indofood CBP Sukses Makmur Tbk.",
                "INDF": "Indofood Sukses Makmur Tbk.",
                "BBNI": "Bank Negara Indonesia Tbk."
            }
            logger.warning(f"Using fallback list of {len(ticker_company_map)} common IDX tickers")
        
        return ticker_company_map
    
    def analyze_article(self, article: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze article with separate LLM requests for sentiment/ticker analysis and summary.
        
        Args:
            article (Dict[str, Any]): Article data including headline and content
            
        Returns:
            Dict[str, Any]: Analysis results including sentiment, tickers and summary
        """
        # Perform sentiment and ticker analysis with truncated content
        analysis_data = self._analyze_sentiment_and_tickers(article)
        
        # Generate summary with separate LLM request using original content
        summary_article = {
            "headline": article.get("original_headline", article.get("headline", "")),
            "content": article.get("original_content", article.get("content", ""))
        }
        
        # Log the character count difference to verify we're using full content for summary
        trunc_len = len(article.get("content", ""))
        orig_len = len(summary_article.get("content", ""))
        if orig_len > trunc_len:
            logger.info(f"Using full content for summary generation: {orig_len} chars vs {trunc_len} chars in truncated version")
        
        # Generate summary with original content
        summary = self.summarizer_service.generate_summary(summary_article)
        
        # Combine results
        analysis_data["summary"] = summary
        
        return analysis_data
    
    def _analyze_sentiment_and_tickers(self, article: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze sentiment and extract tickers from article with truncated content.
        
        Args:
            article (Dict[str, Any]): Article data including headline and content
            
        Returns:
            Dict[str, Any]: Analysis data with sentiment and tickers
        """
        headline = article.get("headline", "")
        content = article.get("content", "")
        
        # Extract tickers from headline if in format "XXXX: ..."
        headline_ticker = None
        headline_ticker_match = re.match(r'^([A-Z]{4}):', headline)
        if headline_ticker_match:
            potential_ticker = headline_ticker_match.group(1)
            if potential_ticker in self.valid_tickers:
                headline_ticker = potential_ticker
                logger.info(f"Found ticker {headline_ticker} in headline")
        
        # Include a subset of the ticker-company mapping in the prompt
        # Select the first 50 items to avoid token limits
        ticker_company_sample = dict(list(self.ticker_company_map.items())[:50])
        ticker_company_json = json.dumps(ticker_company_sample, ensure_ascii=False)
        
        # Create a prompt for sentiment and ticker analysis
        system_prompt = f"""
        You are a professional financial analyst specializing in Indonesian financial news. Perform the following two tasks based on the article content:

        1. SENTIMENT ANALYSIS:
        - Classify the sentiment as "positive", "neutral", or "negative"
        - Provide a confidence score as a float between 0.0 and 1.0

        2. TICKER EXTRACTION:
        - Identify up to 5 Indonesian stock tickers (IDX-listed) that are either explicitly mentioned or strongly implied based on the headline or content
        - Only include official ticker symbols listed on the Indonesia Stock Exchange (IDX)
        - If you see a ticker format at the beginning of the headline (like "XXXX: ..."), prioritize this ticker
        - Below is a partial list of valid IDX ticker symbols with their company names:
          {ticker_company_json}
        - Provide a brief explanation (in Bahasa Indonesia) for why each ticker is relevant to the article
        - DO NOT hallucinate or make up ticker symbols that are not in the IDX listing

        Output format:
        Return only a JSON object with the following structure:
        {{
        "sentiment": "positive" | "neutral" | "negative",
        "confidence": 0.0-1.0,
        "tickers": ["BBCA", "TLKM"],
        "reasoning": "BBCA disebutkan secara eksplisit terkait kinerja keuangan kuartalan, sementara TLKM relevan karena kerjasama strategis dalam proyek digitalisasi."
        }}

        - Do not invent tickers that are not valid in the IDX or not in the provided reference.
        - If there are no relevant tickers, return an empty array: "tickers": [], and explain accordingly in the reasoning.
        - Ensure all text in "reasoning" is written in Bahasa Indonesia.
        """
        
        # Customize user prompt with headline ticker hint if available
        user_prompt = f"""
        Judul Berita: {headline}

        Isi Berita: {content}
        """
        
        if headline_ticker:
            user_prompt += f"\n\nCatatan: Ticker {headline_ticker} ({self.ticker_company_map.get(headline_ticker, '')}) terdeteksi dalam judul berita dan kemungkinan besar relevan."
        
        user_prompt += "\n\nAnalisis sentimen dan ekstraksi ticker saham artikel berita keuangan ini dalam format JSON."
        
        try:
            # Use a balanced temperature for analysis
            result = self.llm_service.generate_completion(
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                temperature=0.2
            )
            
            # Parse the JSON response
            json_pattern = result.strip()
            if not json_pattern.startswith("{"):
                # Find the first occurrence of a JSON-like pattern
                json_match = re.search(r'\{.*\}', result, re.DOTALL)
                if json_match:
                    json_pattern = json_match.group(0)
            
            analysis_data = json.loads(json_pattern)
            
            # Validate and normalize the results
            validated_data = self._validate_results(analysis_data, headline_ticker)
            
            return validated_data
            
        except Exception as e:
            logger.error(f"Error in sentiment and ticker analysis: {str(e)}")
            # Return default values if analysis fails
            default_tickers = [headline_ticker] if headline_ticker else []
            return {
                "sentiment": "neutral",
                "confidence": 0.5,
                "tickers": default_tickers,
                "reasoning": "Error dalam proses analisis."
            }
    
    def _validate_results(self, data: Dict[str, Any], headline_ticker: str = None) -> Dict[str, Any]:
        """
        Validate and normalize the analysis results, ensuring only valid tickers are included.
        
        Args:
            data (Dict[str, Any]): Raw analysis data from LLM
            headline_ticker (str, optional): Ticker extracted from headline if any
            
        Returns:
            Dict[str, Any]: Validated analysis data
        """
        validated = {}
        
        # Validate sentiment
        if "sentiment" not in data or data["sentiment"].lower() not in SENTIMENT_OPTIONS:
            logger.warning(f"Invalid sentiment value: {data.get('sentiment')}. Defaulting to 'neutral'.")
            validated["sentiment"] = "neutral"
        else:
            validated["sentiment"] = data["sentiment"].lower()
        
        # Validate confidence
        if "confidence" not in data or not isinstance(data["confidence"], (int, float)):
            logger.warning("Invalid confidence value. Defaulting to 0.5.")
            validated["confidence"] = 0.5
        else:
            # Ensure confidence is between 0 and 1
            validated["confidence"] = max(0.0, min(1.0, float(data["confidence"])))
        
        # Validate tickers
        if "tickers" not in data or not isinstance(data["tickers"], list):
            logger.warning("Invalid tickers value. Defaulting to empty list.")
            validated["tickers"] = []
        else:
            # Process tickers and keep only those that are valid
            processed_tickers = []
            for ticker in data["tickers"]:
                standardized = self._standardize_ticker(ticker)
                if standardized in self.valid_tickers:
                    processed_tickers.append(standardized)
                else:
                    logger.warning(f"Removed invalid ticker: {standardized}")
            
            # Make sure headline ticker is included if it exists
            if headline_ticker and headline_ticker not in processed_tickers:
                processed_tickers.insert(0, headline_ticker)
                logger.info(f"Added headline ticker {headline_ticker} to results")
            
            # Limit to 5 tickers
            validated["tickers"] = processed_tickers[:5]
        
        # Validate reasoning
        if "reasoning" not in data or not isinstance(data["reasoning"], str):
            logger.warning("Invalid reasoning. Defaulting to empty string.")
            validated["reasoning"] = ""
        else:
            validated["reasoning"] = data["reasoning"]
        
        return validated
    
    def _standardize_ticker(self, ticker: str) -> str:
        """
        Standardize the ticker symbol format.
        
        Args:
            ticker (str): Raw ticker symbol
            
        Returns:
            str: Standardized ticker symbol (uppercase, no spaces)
        """
        # Remove any non-alphanumeric characters except period (for BRK.A format)
        ticker = re.sub(r'[^A-Za-z0-9.]', '', ticker)
        return ticker.upper().strip()