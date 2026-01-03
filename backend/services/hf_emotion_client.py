import os
from typing import Any, List, Dict
from dotenv import load_dotenv
import requests

# Load environment variables
load_dotenv('../.env')

HF_TOKEN = os.getenv("HF_TOKEN", "")

if not HF_TOKEN:
    raise ValueError("HF_TOKEN environment variable is required. Please set it in the root .env file")

# Using SamLowe/roberta-base-go_emotions - popular and fine-tuned for 27 emotions + neutral
# High accuracy model trained on GoEmotions dataset
# Using router endpoint (router.huggingface.co) as api-inference is deprecated
EMOTION_MODEL = "SamLowe/roberta-base-go_emotions"
EMOTION_URL = f"https://router.huggingface.co/hf-inference/models/{EMOTION_MODEL}"
HEADERS = {
    "Authorization": f"Bearer {HF_TOKEN}",
    "Content-Type": "application/json",
}


def classify_emotions(text: str) -> List[Dict[str, Any]]:
    """
    Call HF Router API for GoEmotions model (27 emotions) using requests.
    Returns list of dicts: [{label, score}, ...] sorted by score.
    
    The GoEmotions model returns a list of all emotions with scores (multi-label classification).
    """
    payload = {"inputs": text}
    try:
        resp = requests.post(EMOTION_URL, headers=HEADERS, json=payload, timeout=30)
        resp.raise_for_status()
        data = resp.json()
        
        # Handle model loading errors
        if isinstance(data, dict) and "error" in data:
            error_msg = data.get("error", "Unknown error")
            if "loading" in error_msg.lower() or "model" in error_msg.lower():
                raise Exception(f"Model loading error: {error_msg}. The model may be initializing. Please try again in a moment.")
            raise Exception(f"API error: {error_msg}")
        
        # Handle different response formats
        # GoEmotions model typically returns a list of dicts with label and score
        if isinstance(data, list):
            # If nested list, unwrap it
            if data and isinstance(data[0], list):
                data = data[0]
            
            # If it's a list of dicts, return as-is (sorted by score if needed)
            if data and isinstance(data[0], dict):
                # Sort by score descending if not already sorted
                if "score" in data[0]:
                    data = sorted(data, key=lambda x: x.get("score", 0), reverse=True)
                return data
        
        # If it's a dict with labels and scores (multi-label format)
        if isinstance(data, dict) and "label" in data:
            # Convert single dict to list
            return [data]
        
        # Fallback: return empty list
        return []
        
    except requests.exceptions.Timeout:
        raise Exception("Emotion model request timed out. The model may be slow to respond.")
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 503:
            raise Exception("Emotion model is currently unavailable. It may be loading. Please try again in a moment.")
        elif e.response.status_code == 410:
            raise Exception(f"Model endpoint unavailable (410). Please check if the model is accessible.")
        raise Exception(f"HTTP error from emotion model: {str(e)}")


