"""
Summarizer service for financial news articles.
Generates concise, financially-focused summaries of articles.
"""

import json
import re
from typing import Dict, Any

from services.llm_service import LLMService
from utils.logger import logger

class SummarizerService:
    """Service for summarizing financial news articles."""
    
    def __init__(self, llm_service: LLMService):
        """
        Initialize the summarizer service.
        
        Args:
            llm_service (LLMService): LLM service for text generation
        """
        self.llm_service = llm_service
    
    def generate_summary(self, article: Dict[str, Any]) -> str:
        """
        Generate a financially focused summary of a news article.
        
        Args:
            article (Dict[str, Any]): Article data with headline and content
            
        Returns:
            str: Concise financial summary of the article
        """
        headline = article.get("headline", "")
        content = article.get("content", "")
        
        # Create a prompt for summarization
        system_prompt = """
        You are a financial news editor who specializes in creating concise, informative summaries.
        Your task is to summarize the given financial news article in 1-3 sentences, focusing on:
        
        1. The key financial or market implications
        2. Specific impacts on companies, sectors, or the broader economy
        3. Any numerical data points that are significant (revenue, growth, market size, etc.)
        4. Potential future implications for investors
        
        CRITICAL FORMATTING REQUIREMENTS:
        - Write ONLY 1-3 complete sentences in Bahasa Indonesia
        - Do NOT include ANY thinking, reasoning or meta-commentary
        - Do NOT use <think> tags or ANY other tags
        - Do NOT include phrases like "Berikut ringkasannya:" or any other introduction
        - NEVER explain your process or reasoning
        - Start your response immediately with the first sentence of the summary
        
        Your summary should be factual, concise, and focused on the financial aspects.
        Do not include personal opinions or recommendations to buy/sell securities.
        
        Example of the EXACT format required:
        "Apple mengumumkan pendapatan kuartalan yang lebih tinggi dari ekspektasi analis, didorong oleh penjualan iPhone yang kuat. Perusahaan melaporkan pendapatan sebesar $123 miliar, naik 10% dibandingkan tahun lalu."
        """
        
        user_prompt = f"""
        Headline: {headline}
        
        Content: {content}
        
        Create a 1-3 sentence financial summary of this article in Bahasa Indonesia.
        ONLY include the final summary without ANY commentary or <think> tags.
        """
        
        try:
            # Use low temperature for more deterministic output
            result = self.llm_service.generate_completion(
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                temperature=0.3
            )
            
            # Clean up the summary
            summary = result.strip()
            
            # Remove any thinking tags and their content
            thinking_pattern = r'<think>[\s\S]*?<\/think>'
            summary = re.sub(thinking_pattern, '', summary, flags=re.IGNORECASE)
            
            # Remove any standalone thinking tags
            summary = re.sub(r'<think>|<\/think>', '', summary, flags=re.IGNORECASE)
            
            # Remove lines with thinking indicators
            thinking_indicators = [
                "Okay, so I need to", 
                "Let me", 
                "I should", 
                "I'll", 
                "I need to",
                "Berikut ringkasannya:",
                "Ringkasan:",
                "Summary:"
            ]
            
            lines = summary.split('\n')
            filtered_lines = []
            for line in lines:
                if not any(indicator.lower() in line.lower() for indicator in thinking_indicators):
                    filtered_lines.append(line)
            
            summary = ' '.join(filtered_lines).strip()
            
            # Ensure proper sentence count (1-3 sentences)
            sentences = re.split(r'[.!?]+', summary)
            sentences = [s.strip() for s in sentences if s.strip()]
            
            if len(sentences) > 3:
                logger.warning("Summary too long, truncating to 3 sentences.")
                summary = '. '.join(sentences[:3]) + '.'
            
            # Final cleanup
            summary = summary.strip()
            
            # Make sure summary ends with proper punctuation
            if summary and summary[-1] not in ['.', '!', '?']:
                summary += '.'
                
            return summary
            
        except Exception as e:
            logger.error(f"Error generating summary: {str(e)}")
            # Return a minimal summary if generation fails
            return f"Artikel tentang: {headline}"