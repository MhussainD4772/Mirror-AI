import requests
import json
import logging
from typing import List, Dict, Any
import os

class ReflectionAI:
    """
    Service for generating empathetic reflection summaries using Mistral-7B-Instruct
    """
    
    def __init__(self):
        self.model_name = "mistralai/Mistral-7B-Instruct"
        self.api_url = f"https://api-inference.huggingface.co/models/{self.model_name}"
        self.hf_token = os.getenv("HF_TOKEN", "")
        self.headers = {
            "Authorization": f"Bearer {self.hf_token}",
            "Content-Type": "application/json"
        }
    
    async def generate_summary(self, text: str, sentiment: str) -> str:
        """
        Generate an empathetic summary of the user's reflection using Mistral-7B-Instruct
        
        Prompt template:
        You are a personal reflection AI.
        Summarize the user's entry in 2–3 sentences with empathy.
        End with one actionable suggestion.
        Return cleaned string.
        """
        try:
            logging.info(f"Generating summary for: {text[:50]}...")
            prompt = self._create_prompt(text, sentiment)
            logging.info(f"Using prompt: {prompt[:100]}...")
            
            payload = {
                "inputs": prompt,
                "parameters": {
                    "max_new_tokens": 150,
                    "temperature": 0.7,
                    "do_sample": True,
                    "return_full_text": False
                }
            }
            
            response = requests.post(
                self.api_url,
                headers=self.headers,
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                logging.info(f"Mistral API response: {result}")
                
                if isinstance(result, list) and len(result) > 0:
                    summary = result[0].get("generated_text", "").strip()
                    cleaned_summary = self._clean_summary(summary)
                    logging.info(f"Generated summary: {cleaned_summary[:50]}...")
                    return cleaned_summary
                else:
                    logging.warning("Unexpected Mistral API response format")
                    return self._fallback_summary(text, sentiment)
            else:
                logging.warning(f"Mistral API error: {response.status_code} - {response.text}")
                return self._fallback_summary(text, sentiment)
                
        except Exception as e:
            logging.error(f"Error generating summary: {str(e)}")
            return self._fallback_summary(text, sentiment)
    
    def _create_prompt(self, text: str, sentiment: str) -> str:
        """
        Create a prompt for empathetic reflection summary
        """
        return f"""You are a personal reflection AI.

User's reflection: "{text}"
Detected sentiment: {sentiment}

Summarize the user's entry in 2–3 sentences with empathy.
End with one actionable suggestion.

Be warm, understanding, and supportive. Avoid clinical language."""

    def _clean_summary(self, summary: str) -> str:
        """
        Clean and format the generated summary
        """
        # Remove any unwanted prefixes or suffixes
        summary = summary.replace("Summary:", "").replace("Reflection:", "").strip()
        
        # Remove quotes if the entire response is wrapped in quotes
        if summary.startswith('"') and summary.endswith('"'):
            summary = summary[1:-1]
        
        # Ensure it ends with a period
        if not summary.endswith(('.', '!', '?')):
            summary += "."
            
        return summary
    
    def _fallback_summary(self, text: str, sentiment: str) -> str:
        """
        Fallback summary when AI model is unavailable
        """
        logging.info("Using fallback summary generation")
        
        sentiment_responses = {
            "positive": "It sounds like you had a good day! You seem to be feeling optimistic about your progress.",
            "negative": "I can sense you're going through a challenging time. Your feelings are valid and important.",
            "neutral": "You've shared a thoughtful reflection about your day. There's value in taking time to process your experiences."
        }
        
        base_response = sentiment_responses.get(sentiment.lower(), sentiment_responses["neutral"])
        return f"{base_response} Consider what small step you might take tomorrow to continue growing."
