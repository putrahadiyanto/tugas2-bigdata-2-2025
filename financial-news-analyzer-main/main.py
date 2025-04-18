import json
import os
import concurrent.futures
from datetime import datetime
from typing import List, Dict, Any
from queue import Queue
from threading import Lock

from config import (
    OUTPUT_FILE, 
    MAX_WORKERS,
    MAX_CONTENT_LENGTH,
    MAX_HEADLINE_LENGTH,
    PRESERVE_START_CHARS,
    PRESERVE_END_CHARS
)
from interfaces.news_loader import load_news_articles
from services.llm_service import LLMService
from services.combined_analysis_service import CombinedAnalysisService
from utils.text_utils import (
    extract_effective_date, 
    normalize_text,
    truncate_text
)
from utils.logger import logger

# Global services to be shared across threads
llm_service = None
combined_analysis_service = None
results_lock = Lock()
file_lock = Lock()  # New lock for file operations

def process_article(article: Dict[str, Any], article_index: int, total_articles: int) -> Dict[str, Any]:
    try:
        logger.info(f"Processing article {article_index+1}/{total_articles}: {article.get('headline', 'No headline')[:50]}...")
        
        # Save original content for summarization
        original_article = {
            'headline': article.get('headline', ''),
            'content': article.get('content', '')
        }
        
        # Normalize text for all processing
        if 'content' in article and article['content']:
            article['content'] = normalize_text(article['content'])
            # Store normalized but not truncated content for summary generation
            normalized_article = {
                'headline': article.get('headline', ''),
                'content': article['content']  # Normalized but not truncated
            }
            
            # Now truncate text for sentiment and ticker analysis
            article['content'] = truncate_text(
                article['content'], 
                MAX_CONTENT_LENGTH, 
                PRESERVE_START_CHARS, 
                PRESERVE_END_CHARS
            )
            
        if 'headline' in article and article['headline']:
            article['headline'] = normalize_text(article['headline'])
            normalized_article['headline'] = article['headline']  # Store normalized headline
            
            article['headline'] = truncate_text(
                article['headline'], 
                MAX_HEADLINE_LENGTH, 
                MAX_HEADLINE_LENGTH, 
                0  # Don't preserve end for headlines
            )
        
        # Extract effective date
        effective_date = extract_effective_date(article)
        
        # Perform combined analysis with separate LLM calls for sentiment/ticker and summary
        logger.info(f"[Article {article_index+1}] Performing analysis...")
        analysis_data = combined_analysis_service.analyze_article({
            # Use truncated content for sentiment and ticker analysis
            "headline": article.get("headline", ""),
            "content": article.get("content", ""),
            # Also pass the normalized but not truncated content for summarization
            "original_content": normalized_article.get("content", ""),
            "original_headline": normalized_article.get("headline", "")
        })
        
        # Compile results
        result = {
            "headline": original_article.get("headline", ""),  # Use original headline
            "effective_date": effective_date.isoformat(),
            "sentiment": analysis_data.get("sentiment", "neutral"),
            "confidence": analysis_data.get("confidence", 0.5),
            "tickers": analysis_data.get("tickers", []),
            "reasoning": analysis_data.get("reasoning", ""),
            "summary": analysis_data.get("summary", "")
        }
        
        logger.info(f"Successfully processed article {article_index+1}: {original_article.get('headline', 'No headline')[:50]}")
        return result
        
    except Exception as e:
        logger.error(f"Error processing article {article_index+1}: {str(e)}")
        # Add minimal information for failed articles
        return {
            "headline": article.get("headline", "Unknown"),
            "error": f"Failed to process: {str(e)}",
            "sentiment": "neutral",
            "confidence": 0.0,
            "tickers": [],
            "reasoning": "Processing error",
            "summary": "Article could not be processed"
        }

def initialize_output_file(article_count: int) -> None:
    """Initialize the output file with metadata."""
    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
    
    metadata = {
        "metadata": {
            "generated_at": datetime.now().isoformat(),
            "article_count": article_count,
            "last_updated": datetime.now().isoformat()
        },
        "results": []
    }
    
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(metadata, f, indent=2, ensure_ascii=False)
    
    logger.info(f"Initialized output file at {OUTPUT_FILE}")

def write_result(result: Dict[str, Any], article_index: int, total_articles: int) -> None:
    """Write a single result to the output file as it's collected."""
    with file_lock:
        try:
            # Read the current file content
            with open(OUTPUT_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Append the new result
            data["results"].append(result)
            
            # Update the last_updated timestamp
            data["metadata"]["last_updated"] = datetime.now().isoformat()
            
            # Write the updated content back to the file
            with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
                
            logger.info(f"Written result for article {article_index+1}/{total_articles} to {OUTPUT_FILE}")
            
        except Exception as e:
            logger.error(f"Error writing result to file: {str(e)}")

def analyze_articles() -> None:
    # Initialize global services
    global llm_service, combined_analysis_service
    
    # Load articles
    logger.info("Loading articles from data file")
    articles = load_news_articles()
    logger.info(f"Loaded {len(articles)} articles")
    
    # Initialize the output file with metadata
    initialize_output_file(len(articles))
    
    # Initialize services
    llm_service = LLMService()
    combined_analysis_service = CombinedAnalysisService(llm_service)
    
    # Track processed articles count
    processed_count = 0
    
    # Process articles in parallel using ThreadPoolExecutor
    with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        # Submit all tasks
        future_to_index = {
            executor.submit(process_article, article, i, len(articles)): i 
            for i, article in enumerate(articles)
        }
        
        # Collect and write results as they complete
        for future in concurrent.futures.as_completed(future_to_index):
            article_index = future_to_index[future]
            try:
                result = future.result()
                write_result(result, article_index, len(articles))
                with results_lock:
                    processed_count += 1
                    logger.info(f"Processed {processed_count}/{len(articles)} articles")
            except Exception as e:
                logger.error(f"Unexpected error with article {article_index+1}: {str(e)}")
    
    logger.info(f"All articles processed. Total: {processed_count}/{len(articles)}")

def main():
    logger.info("Starting Financial News Analyzer")
    logger.info(f"Using {MAX_WORKERS} worker threads for parallel processing")
    
    try:
        # Analyze articles and write results immediately
        analyze_articles()
        
        logger.info(f"Analysis complete. Results saved to {OUTPUT_FILE}")
        
    except Exception as e:
        logger.error(f"Application error: {str(e)}")
        raise

if __name__ == "__main__":
    main()