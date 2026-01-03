import logging
from typing import List, Dict, Any
import re

from .hf_tagging_client import classify_tags

class ThemeExtractor:
    """
    Service for extracting themes and tags using BART-large-MNLI
    """
    
    def __init__(self):
        self.model_name = "facebook/bart-large-mnli"
        
        # Candidate labels as specified in requirements
        self.candidate_labels = [
            "work", "gym", "coding", "learning", "stress", "discipline", 
            "motivation", "family", "friends", "sleep", "burnout"
        ]
    
    async def extract_themes(self, text: str) -> List[str]:
        """
        Extract relevant themes/tags from the reflection text using BART-large-MNLI
        
        Use model: facebook/bart-large-mnli
        Candidate labels = ["work", "gym", "coding", "learning", "stress", "discipline", "motivation", "family", "friends", "sleep", "burnout"]
        Return list of top 3 relevant labels.
        """
        try:
            logging.info(f"Extracting themes for: {text[:50]}...")
            
            # First try using BART for zero-shot classification
            themes = await self._classify_with_bart(text)
            
            # If BART fails or returns few results, use keyword extraction
            if len(themes) < 2:
                keyword_themes = self._extract_keywords(text)
                themes.extend(keyword_themes)
            
            # Remove duplicates and limit to top 3 themes
            unique_themes = list(dict.fromkeys(themes))[:3]
            logging.info(f"Extracted themes: {unique_themes}")
            
            return unique_themes
            
        except Exception as e:
            logging.error(f"Error extracting themes: {str(e)}")
            return self._extract_keywords(text)[:3]
    
    async def _classify_with_bart(self, text: str) -> List[str]:
        """
        Use BART-large-MNLI for zero-shot classification
        """
        try:
            logging.info(f"Using BART classification with labels: {self.candidate_labels}")
            
            response = classify_tags(text, self.candidate_labels)
            
            logging.info(f"BART API response: {response}")

            themes = []
            
            # Handle list of dicts format: [{'label': 'work', 'score': 0.9}, ...]
            if isinstance(response, list):
                for item in response:
                    if isinstance(item, dict) and "label" in item and "score" in item:
                        if item["score"] > 0.3:
                            themes.append(item["label"])
                logging.info(f"BART themes (score > 0.3): {themes}")
                return themes
            
            # Handle dict format: {'labels': [...], 'scores': [...]}
            if isinstance(response, dict) and "labels" in response and "scores" in response:
                for label, score in zip(response["labels"], response["scores"]):
                    if score > 0.3:
                        themes.append(label)
                logging.info(f"BART themes (score > 0.3): {themes}")
                return themes

            logging.warning("Unexpected BART API response format: %s", response)
            return []
        except Exception as e:
            logging.error(f"BART classification error: {str(e)}")
            return []
    
    def _extract_keywords(self, text: str) -> List[str]:
        """
        Fallback keyword-based theme extraction
        """
        logging.info("Using fallback keyword extraction")
        text_lower = text.lower()
        extracted_themes = []
        
        # Theme keyword mappings based on candidate labels
        theme_keywords = {
            "work": [
                "work", "job", "career", "office", "meeting", "project", "deadline",
                "boss", "colleague", "promotion", "interview", "resume", "business"
            ],
            "gym": [
                "gym", "workout", "exercise", "fitness", "training", "running", 
                "weight", "cardio", "muscle", "strength", "physical"
            ],
            "coding": [
                "code", "coding", "programming", "development", "software", "debug",
                "algorithm", "function", "variable", "github", "repository", "devfolio"
            ],
            "learning": [
                "learn", "learning", "study", "education", "course", "book", "tutorial",
                "knowledge", "skill", "practice", "improve", "progress"
            ],
            "stress": [
                "stress", "stressed", "pressure", "overwhelmed", "anxiety", "worried",
                "tension", "burden", "strain", "difficult", "challenging"
            ],
            "discipline": [
                "discipline", "routine", "habit", "consistency", "commitment", "focus",
                "dedication", "perseverance", "self-control", "willpower"
            ],
            "motivation": [
                "motivation", "motivated", "inspired", "drive", "passion", "enthusiasm",
                "energy", "excitement", "determination", "ambition"
            ],
            "family": [
                "family", "parent", "mother", "father", "sibling", "brother", "sister",
                "relative", "home", "household", "domestic"
            ],
            "friends": [
                "friend", "friends", "buddy", "pal", "social", "hangout", "party",
                "relationship", "companion", "acquaintance"
            ],
            "sleep": [
                "sleep", "sleeping", "tired", "exhausted", "rest", "bed", "night",
                "insomnia", "fatigue", "drowsy", "nap"
            ],
            "burnout": [
                "burnout", "burned out", "exhausted", "drained", "overworked", "fatigue",
                "depleted", "empty", "tired", "weary"
            ]
        }
        
        # Check for theme matches
        for theme, keywords in theme_keywords.items():
            if any(keyword in text_lower for keyword in keywords):
                extracted_themes.append(theme)
        
        logging.info(f"Keyword-extracted themes: {extracted_themes}")
        return extracted_themes
