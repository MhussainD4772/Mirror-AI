import logging
from typing import List, Dict, Any, Optional

from .hf_summary_client import generate_summary as hf_generate_summary

class ReflectionAI:
    """
    Service for generating empathetic reflection summaries using Mistral-7B-Instruct
    """
    
    def __init__(self):
        self.model_name = "mistralai/Mistral-7B-Instruct"
        self.timeout_seconds = 30
    
    async def generate_summary(
        self,
        text: str,
        dominant_emotion: str,
        top_emotions: Optional[List[Dict[str, Any]]] = None
    ) -> str:
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
            prompt = self._create_prompt(text, dominant_emotion, top_emotions)
            logging.info(f"Using prompt: {prompt[:100]}...")
            
            summary = hf_generate_summary(prompt)
            cleaned_summary = self._clean_summary(summary or "")
            logging.info(f"Generated summary: {cleaned_summary[:50]}...")
            return cleaned_summary
        except Exception as e:
            logging.error(f"Mistral API failure: {str(e)}")
            return self._fallback_summary(text, dominant_emotion)
    
    def _create_prompt(
        self,
        text: str,
        dominant_emotion: str,
        top_emotions: Optional[List[Dict[str, Any]]] = None
    ) -> str:
        """
        Create a prompt for empathetic reflection summary
        """
        emotion_line = f"Detected dominant emotion: {dominant_emotion}"
        if top_emotions:
            formatted_top = ", ".join(
                emotion.get("label", "")
                for emotion in top_emotions[:3]
                if emotion.get("label")
            )
            if formatted_top:
                emotion_line += f" (also present: {formatted_top})"

        return f"""You are a personal reflection AI.

User's reflection: "{text}"
{emotion_line}

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
    
    def _fallback_summary(self, text: str, dominant_emotion: str) -> str:
        """
        Fallback summary when AI model is unavailable
        """
        logging.info("Using fallback summary generation")
        
        emotion_responses = {
            "joy": "It sounds like you had a bright moment that filled you with joy. Celebrate the good energy you're carrying.",
            "gratitude": "You're noticing what matters to you, and that gratitude is powerful for your growth.",
            "love": "You're connecting deeply with what you care about, and that warmth can keep guiding you.",
            "pride": "You’re recognizing your own progress, and that pride is well-deserved.",
            "optimism": "You're holding an encouraging outlook, and that optimism can help shape tomorrow.",
            "relief": "You're feeling a sense of relief, which shows how much you've been carrying.",
            "anger": "You're feeling some frustration, and it's important to acknowledge that tension.",
            "sadness": "You're moving through a tender moment. It's okay to feel vulnerable.",
            "fear": "There's anxiety in what you're experiencing, and that worry deserves compassion.",
            "grief": "You're holding a heavy loss, and it's valid to sit with that grief.",
            "confusion": "Things feel uncertain right now, and it makes sense that you're searching for clarity.",
            "neutral": "You've shared a thoughtful reflection about your day. There's value in taking time to process your experiences.",
        }
        
        base_response = emotion_responses.get(
            dominant_emotion.lower(), emotion_responses["neutral"]
        )
        return f"{base_response} Consider what small step you might take tomorrow to continue growing."
