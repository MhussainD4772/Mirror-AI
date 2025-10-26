import requests
import json
import logging
import os
from typing import Dict, Any

class SentimentAnalyzer:
    """
    Service for sentiment analysis using twitter-roberta-base-sentiment-latest
    """
    
    def __init__(self):
        self.model_name = "cardiffnlp/twitter-roberta-base-sentiment-latest"
        self.api_url = f"https://api-inference.huggingface.co/models/{self.model_name}"
        self.hf_token = os.getenv("HF_TOKEN", "")
        self.headers = {
            "Authorization": f"Bearer {self.hf_token}",
            "Content-Type": "application/json"
        }
    
    async def analyze(self, text: str) -> str:
        """
        Analyze sentiment of the input text using Hugging Face API
        Returns: 'positive' | 'neutral' | 'negative'
        """
        try:
            logging.info(f"Analyzing sentiment for: {text[:50]}...")
            
            # Call HF Inference API
            payload = {
                "inputs": text,
                "parameters": {
                    "return_all_scores": True
                }
            }
            
            response = requests.post(
                self.api_url,
                headers=self.headers,
                json=payload,
                timeout=15
            )
            
            if response.status_code == 200:
                result = response.json()
                logging.info(f"HF API response: {result}")
                
                if isinstance(result, list) and len(result) > 0:
                    scores = result[0]
                    sentiment = self._interpret_scores(scores)
                    logging.info(f"Sentiment result: {sentiment}")
                    return sentiment
                else:
                    logging.warning("Unexpected HF API response format")
                    return self._fallback_sentiment(text)
            else:
                logging.warning(f"HuggingFace API error: {response.status_code} - {response.text}")
                return self._fallback_sentiment(text)
                
        except Exception as e:
            logging.error(f"Error analyzing sentiment: {str(e)}")
            return self._fallback_sentiment(text)
    
    def _interpret_scores(self, scores: list) -> str:
        """
        Interpret sentiment scores and return the dominant sentiment
        """
        # Find the highest scoring sentiment
        max_score = 0
        dominant_sentiment = "neutral"
        
        for score_dict in scores:
            label = score_dict.get("label", "").lower()
            score = score_dict.get("score", 0)
            
            if score > max_score:
                max_score = score
                dominant_sentiment = label
        
        # Map HuggingFace labels to our labels
        sentiment_mapping = {
            "positive": "positive",
            "negative": "negative", 
            "neutral": "neutral",
            "label_0": "negative",  # Some models use numeric labels
            "label_1": "neutral",
            "label_2": "positive",
            "label_1_positive": "positive",
            "label_2_negative": "negative",
            "label_0_neutral": "neutral"
        }
        
        mapped_sentiment = sentiment_mapping.get(dominant_sentiment, "neutral")
        logging.info(f"Mapped sentiment: {dominant_sentiment} -> {mapped_sentiment}")
        return mapped_sentiment
    
    def _fallback_sentiment(self, text: str) -> str:
        """
        Simple fallback sentiment analysis using keyword matching
        Used when HF API is unavailable or fails
        """
        logging.info("Using fallback sentiment analysis")
        
        positive_words = [
            "good", "great", "amazing", "wonderful", "excellent", "happy", 
            "joy", "love", "excited", "proud", "accomplished", "grateful",
            "blessed", "lucky", "successful", "progress", "improvement",
            "fantastic", "awesome", "brilliant", "perfect", "delighted"
        ]
        
        negative_words = [
            "bad", "terrible", "awful", "sad", "angry", "frustrated", 
            "disappointed", "worried", "anxious", "stressed", "tired",
            "exhausted", "overwhelmed", "depressed", "lonely", "hurt",
            "horrible", "disgusting", "hate", "annoyed", "upset"
        ]
        
        text_lower = text.lower()
        
        positive_count = sum(1 for word in positive_words if word in text_lower)
        negative_count = sum(1 for word in negative_words if word in text_lower)
        
        if positive_count > negative_count:
            return "positive"
        elif negative_count > positive_count:
            return "negative"
        else:
            return "neutral"
