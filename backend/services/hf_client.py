import logging
import os
import time
from typing import Any, Dict, Optional

import requests

HF_TOKEN = os.getenv("HF_TOKEN", "")
HF_BASE_URL = "https://api-inference.huggingface.co/models"

HEADERS = {
    "Authorization": f"Bearer {HF_TOKEN}",
    "Content-Type": "application/json",
}


def call_hf_model(
    model_name: str,
    inputs: Any,
    parameters: Optional[Dict[str, Any]] = None,
    *,
    max_retries: int = 3,
    timeout: int = 20,
) -> Any:
    """
    Universal Hugging Face inference caller with retries and basic logging.
    """
    if not HF_TOKEN:
        raise RuntimeError("HF_TOKEN environment variable is not set.")

    if not model_name:
        raise ValueError("Model name must be provided.")

    url = f"{HF_BASE_URL}/{model_name}"
    payload: Dict[str, Any] = {"inputs": inputs}
    if parameters:
        payload["parameters"] = parameters

    for attempt in range(1, max_retries + 1):
        try:
            response = requests.post(
                url, headers=HEADERS, json=payload, timeout=timeout
            )

            if response.status_code == 200:
                return response.json()

            logging.warning(
                "[HF] Attempt %s: HTTP %s → %.100s",
                attempt,
                response.status_code,
                response.text,
            )

        except Exception as exc:  # pragma: no cover - network failures
            logging.warning("[HF] Attempt %s raised exception: %s", attempt, exc)

        if attempt < max_retries:
            time.sleep(attempt * 2)

    raise RuntimeError(
        f"Hugging Face inference failed after {max_retries} attempts for {model_name}"
    )

