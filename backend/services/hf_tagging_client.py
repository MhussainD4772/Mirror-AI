import os
from typing import Any, Dict, List

import requests

TAGGING_MODEL = "facebook/bart-large-mnli"
TAGGING_URL = f"https://router.huggingface.co/hf-inference/models/{TAGGING_MODEL}"
HEADERS = {"Authorization": f"Bearer {os.environ['HF_TOKEN']}", "Content-Type": "application/json"}


def classify_tags(text: str, candidate_labels: List[str]) -> Dict[str, Any]:
    payload: Dict[str, Any] = {
        "inputs": text,
        "parameters": {"candidate_labels": candidate_labels, "multi_label": True},
    }
    response = requests.post(TAGGING_URL, headers=HEADERS, json=payload, timeout=20)
    response.raise_for_status()
    return response.json()


