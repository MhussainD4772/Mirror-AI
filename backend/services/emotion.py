import logging
from typing import Any, Dict, List, Tuple

from .hf_emotion_client import classify_emotions


class EmotionAnalyzer:
    """
    Service for multi-emotion analysis using the GoEmotions fine-tuned model.
    """

    def __init__(self) -> None:
        self.model_name = "SamLowe/roberta-base-go_emotions"  # Popular GoEmotions model with 27 emotions + neutral
        self.timeout_seconds = 30  # Increased for GoEmotions model
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
        print(f"[EMOTION] Analyzing emotions via GoEmotions model for text: {text[:50]}...")
        logging.info("Analyzing emotions via GoEmotions model...")

        try:
            response = classify_emotions(text)
            print(f"[EMOTION] API response: {str(response)[:300]}")
            logging.info(f"Emotion API response (first 200 chars): {str(response)[:200]}")
            result = self._parse_response(response)
            print(f"[EMOTION] Parsed - dominant: {result.get('dominant_emotion')}, top: {result.get('top_emotions')}")
            logging.info(f"Parsed dominant emotion: {result.get('dominant_emotion')}, top emotions: {result.get('top_emotions')}")
            return result
        except Exception as exc:  # pragma: no cover - unexpected edge cases
            print(f"[EMOTION] API FAILED: {exc}")
            logging.error("GoEmotions API failure (router v2): %s", exc)
            print("[EMOTION] Using fallback heuristic analysis")
            logging.warning("Falling back to heuristic emotion analysis.")
            fallback_result = self._fallback_analysis(text)
            print(f"[EMOTION] Fallback result - dominant: {fallback_result.get('dominant_emotion')}, top: {fallback_result.get('top_emotions')}")
            return fallback_result

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
        # Map GoEmotions label variations to our standard emotion names
        label_mapping = {
            "admiration": "admiration",
            "amusement": "amusement",
            "anger": "anger",
            "annoyance": "annoyance",
            "approval": "approval",
            "caring": "caring",
            "confusion": "confusion",
            "curiosity": "curiosity",
            "desire": "desire",
            "disappointment": "disappointment",
            "disapproval": "disapproval",
            "disgust": "disgust",
            "embarrassment": "embarrassment",
            "excitement": "excitement",
            "fear": "fear",
            "gratitude": "gratitude",
            "grief": "grief",
            "joy": "joy",
            "love": "love",
            "nervousness": "nervousness",
            "optimism": "optimism",
            "pride": "pride",
            "realization": "realization",
            "relief": "relief",
            "remorse": "remorse",
            "sadness": "sadness",
            "surprise": "surprise",
            "neutral": "neutral",
        }
        
        for entry in scores:
            label = entry.get("label")
            score = entry.get("score")
            if label is None or score is None:
                continue
            
            # Normalize label: lowercase, replace underscores with spaces, strip
            normalized_label = label.lower().replace("_", " ").strip()
            
            # Map to our standard emotion name
            mapped_label = label_mapping.get(normalized_label, normalized_label)
            
            # If we have a score for this emotion, use the max (in case of duplicates)
            if mapped_label in self.known_emotions:
                emotion_scores[mapped_label] = max(emotion_scores.get(mapped_label, 0.0), float(score))

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
            "guilt": ["guilty", "guilt", "regret", "remorse", "ashamed", "embarrassment", "embarrassed", "disappointed in myself", "terrible"],
            "disappointment": ["disappointment", "disappointed", "let down", "failed", "forgot", "forgotten"],
            "gratitude": ["grateful", "gratitude", "thankful", "appreciate", "understanding"],
            "pride": ["proud", "pride", "achievement", "successful", "praised"],
            "sadness": ["sad", "down", "blue", "tear", "alone", "depressed", "breakup"],
            "anxiety": ["anxious", "anxiety", "worried", "nervous", "stress"],
            "relief": ["relieved", "relief", "phew", "finally"],
            "joy": ["happy", "joy", "excited", "glad"],
            "anger": ["angry", "mad", "furious", "annoyed", "irritated"],
            "fear": ["afraid", "scared", "worried"],
        }

        text_lower = text.lower()
        emotion_scores = {emotion: 0.0 for emotion in self.known_emotions}
        
        # Count keyword matches - prioritize negative emotions if present
        for emotion, keywords in heuristics.items():
            matches = sum(1 for keyword in keywords if keyword in text_lower)
            if matches > 0:
                # Give higher weight to guilt/disappointment if present
                weight = 0.5 if emotion in ["guilt", "disappointment", "remorse"] else 0.3
                emotion_scores[emotion] = float(matches) * weight

        # If no emotions detected, use neutral
        if sum(emotion_scores.values()) == 0:
            emotion_scores["neutral"] = 1.0
        else:
            # Normalize scores to 0-1 range
            max_score = max(emotion_scores.values())
            if max_score > 0:
                for emotion in emotion_scores:
                    emotion_scores[emotion] = emotion_scores[emotion] / max_score

        dominant_emotion, top_emotions = self._extract_top_emotions(emotion_scores)
        print(f"[FALLBACK] Detected emotions - dominant: {dominant_emotion}, scores: {dict(list(emotion_scores.items())[:5])}")
        return {
            "emotions": emotion_scores,
            "dominant_emotion": dominant_emotion,
            "top_emotions": [
                {"label": label, "score": score} for label, score in top_emotions
            ],
        }

