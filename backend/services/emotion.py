import logging
from typing import Any, Dict, List, Tuple

from .hf_emotion_client import classify_emotions


class EmotionAnalyzer:
    """
    Service for multi-emotion analysis using the GoEmotions fine-tuned model.
    """

    def __init__(self) -> None:
        self.model_name = "bhadresh-savani/bert-base-uncased-emotion"
        self.timeout_seconds = 15
        self.max_retries = 3
        self.known_emotions = [
            "admiration",
            "amusement",
            "anger",
            "annoyance",
            "approval",
            "caring",
            "confusion",
            "curiosity",
            "desire",
            "disappointment",
            "disapproval",
            "disgust",
            "embarrassment",
            "excitement",
            "fear",
            "gratitude",
            "grief",
            "joy",
            "love",
            "nervousness",
            "optimism",
            "pride",
            "realization",
            "relief",
            "remorse",
            "sadness",
            "surprise",
            "neutral",
        ]

    async def analyze(self, text: str) -> Dict[str, Any]:
        """
        Analyze emotions for the provided text via HF router v2.
        Returns:
            {
                "emotions": {emotion: probability},
                "dominant_emotion": str,
                "top_emotions": [{"label": str, "score": float}, ...]
            }
        """
        logging.info("Analyzing emotions via GoEmotions model...")

        try:
            response = classify_emotions(text)
            return self._parse_response(response)
        except Exception as exc:  # pragma: no cover - unexpected edge cases
            logging.error("GoEmotions API failure (router v2): %s", exc)

        logging.warning("Falling back to heuristic emotion analysis.")
        return self._fallback_analysis(text)

    def _parse_response(self, response: Any) -> Dict[str, Any]:
        """
        Parse the HF response into the desired structure.
        """
        if not isinstance(response, list) or not response:
            logging.warning("Unexpected GoEmotions response format: %s", response)
            return self._fallback_analysis("")

        scores = response  # hf_hub InferenceClient returns list[dict] directly
        if not isinstance(scores, list):
            logging.warning("Unexpected GoEmotions scores payload: %s", scores)
            return self._fallback_analysis("")

        emotion_scores: Dict[str, float] = {}
        for entry in scores:
            label = entry.get("label")
            score = entry.get("score")
            if label is None or score is None:
                continue
            normalized_label = label.lower()
            emotion_scores[normalized_label] = float(score)

        # Ensure all known emotions exist in the map
        for emotion in self.known_emotions:
            emotion_scores.setdefault(emotion, 0.0)

        dominant_emotion, top_emotions = self._extract_top_emotions(emotion_scores)

        return {
            "emotions": emotion_scores,
            "dominant_emotion": dominant_emotion,
            "top_emotions": [
                {"label": label, "score": score} for label, score in top_emotions
            ],
        }

    def _extract_top_emotions(
        self, emotion_scores: Dict[str, float]
    ) -> Tuple[str, List[Tuple[str, float]]]:
        sorted_emotions = sorted(
            emotion_scores.items(), key=lambda item: item[1], reverse=True
        )
        top_emotions = sorted_emotions[:3]
        dominant_emotion = top_emotions[0][0] if top_emotions else "neutral"
        return dominant_emotion, top_emotions

    def _fallback_analysis(self, text: str) -> Dict[str, Any]:
        """
        Provide a minimal heuristic-based emotion estimate when the API fails.
        """
        heuristics = {
            "joy": ["happy", "joy", "grateful", "excited", "proud", "glad"],
            "sadness": ["sad", "down", "blue", "tear", "alone", "depressed"],
            "anger": ["angry", "mad", "furious", "annoyed", "irritated"],
            "fear": ["afraid", "scared", "worried", "anxious", "nervous"],
            "relief": ["relieved", "phew", "finally", "safe"],
        }

        text_lower = text.lower()
        emotion_scores = {emotion: 0.0 for emotion in self.known_emotions}
        emotion_scores["neutral"] = 1.0

        for emotion, keywords in heuristics.items():
            score = sum(1 for keyword in keywords if keyword in text_lower)
            if score > 0:
                emotion_scores[emotion] = float(score)
                emotion_scores["neutral"] = 0.0

        dominant_emotion, top_emotions = self._extract_top_emotions(emotion_scores)
        return {
            "emotions": emotion_scores,
            "dominant_emotion": dominant_emotion,
            "top_emotions": [
                {"label": label, "score": score} for label, score in top_emotions
            ],
        }

