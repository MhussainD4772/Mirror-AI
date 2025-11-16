import os
from typing import Any, List, Dict

import requests

EMOTION_MODEL = "bhadresh-savani/distilbert-base-uncased-emotion"
EMOTION_URL = f"https://router.huggingface.co/hf-inference/models/{EMOTION_MODEL}"
HEADERS = {
    "Authorization": f"Bearer {os.environ['HF_TOKEN']}",
    "Content-Type": "application/json",
}


def classify_emotions(text: str) -> List[Dict[str, Any]]:
    """
    Call HF router v2 (models endpoint) for text classification.
    Returns list of dicts: [{label, score}, ...]
    """
    payload = {"inputs": text}
    resp = requests.post(EMOTION_URL, headers=HEADERS, json=payload, timeout=20)
    resp.raise_for_status()
    data = resp.json()
    # Expected router payload for classification is a list[dict]
    # Some models may return [[{label, score}, ...]]; normalize.
    if isinstance(data, list) and data and isinstance(data[0], list):
        return data[0]
    return data if isinstance(data, list) else []


