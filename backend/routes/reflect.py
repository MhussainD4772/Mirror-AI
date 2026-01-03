from fastapi import APIRouter, HTTPException, Header
from pydantic import BaseModel, Field
from typing import Dict, List, Optional
from services.reflection_ai import ReflectionAI
from services.emotion import EmotionAnalyzer
from services.tagging import ThemeExtractor
from services.auth_utils import get_user_id_from_token
from supabase_client import SupabaseClient
from datetime import datetime
import logging

router = APIRouter()

# Initialize services
reflection_ai = ReflectionAI()
emotion_analyzer = EmotionAnalyzer()
theme_extractor = ThemeExtractor()
supabase_client = SupabaseClient()

EMOTION_POLARITY_MAP = {
    "admiration": "positive",
    "amusement": "positive",
    "approval": "positive",
    "caring": "positive",
    "curiosity": "positive",
    "desire": "positive",
    "excitement": "positive",
    "gratitude": "positive",
    "joy": "positive",
    "love": "positive",
    "optimism": "positive",
    "pride": "positive",
    "relief": "positive",
    "surprise": "neutral",
    "realization": "neutral",
    "confusion": "neutral",
    "neutral": "neutral",
    "anger": "negative",
    "annoyance": "negative",
    "disapproval": "negative",
    "disappointment": "negative",
    "disgust": "negative",
    "embarrassment": "negative",
    "fear": "negative",
    "grief": "negative",
    "nervousness": "negative",
    "remorse": "negative",
    "sadness": "negative",
}


def map_emotion_to_sentiment(emotion: str) -> str:
    return EMOTION_POLARITY_MAP.get(emotion.lower(), "neutral")

class ReflectionRequest(BaseModel):
    text: str

class EmotionScore(BaseModel):
    label: str
    score: float

class ReflectionResponse(BaseModel):
    summary: str
    dominant_emotion: str
    emotions: Dict[str, float] = Field(default_factory=dict)
    top_emotions: List[EmotionScore] = Field(default_factory=list)
    tags: List[str] = Field(default_factory=list)
    created_at: str
    entry_id: str
    sentiment: Optional[str] = None  # Legacy compatibility

@router.post("/reflect", response_model=ReflectionResponse)
async def process_reflection(
    request: ReflectionRequest,
    authorization: Optional[str] = Header(None)
):
    """
    Process a user's reflection text through AI analysis pipeline
    
    Requires authentication via Authorization header: Bearer <token>
    
    Input: {"text": "Got a lot done in Devfolio but skipped gym again."}
    Process:
    1. Validate user token and extract user_id
    2. Run emotion analysis → 27-emotion probability distribution
    3. Run reflection → short empathetic summary + actionable nudge
    4. Run tag extraction → list of themes (coding, gym, discipline)
    5. Insert record into Supabase table `entries` with user_id
    6. Return full JSON with emotion spectrum
    """
    try:
        # Get authenticated user_id from token
        user_id = get_user_id_from_token(authorization)
        
        # Validate input
        if not request.text.strip():
            raise HTTPException(status_code=400, detail="Reflection text cannot be empty")
        
        logging.info(f"Processing reflection for user {user_id}: {request.text[:50]}...")
        
        # 1. Emotion Analysis
        emotion_result = await emotion_analyzer.analyze(request.text)
        dominant_emotion = emotion_result.get("dominant_emotion", "neutral")
        emotions = emotion_result.get("emotions", {})
        top_emotions = emotion_result.get("top_emotions", [])
        logging.info(
            "Emotion analysis complete. Dominant emotion: %s | Top emotions: %s",
            dominant_emotion,
            top_emotions,
        )
        
        # 2. Generate empathetic summary
        summary = await reflection_ai.generate_summary(
            request.text, dominant_emotion, top_emotions
        )
        logging.info(f"Summary generated: {summary[:50]}...")
        
        # 3. Extract themes/tags
        tags = await theme_extractor.extract_themes(request.text)
        logging.info(f"Tags extracted: {tags}")
        
        # 4. Save to database
        legacy_sentiment = map_emotion_to_sentiment(dominant_emotion)

        entry_data = {
            "user_id": user_id,
            "text": request.text,
            "ai_summary": summary,
            "sentiment": legacy_sentiment,
            "dominant_emotion": dominant_emotion,
            "emotions": emotions,
            "tags": tags,
            "created_at": datetime.utcnow().isoformat()
        }
        
        # Extract token from authorization header for RLS
        token = None
        if authorization:
            parts = authorization.split()
            if len(parts) == 2 and parts[0].lower() == "bearer":
                token = parts[1]
        
        entry_id = await supabase_client.save_reflection(entry_data, access_token=token)
        logging.info(f"Entry saved with ID: {entry_id}")
        
        return ReflectionResponse(
            summary=summary,
            dominant_emotion=dominant_emotion,
            emotions=emotions,
            top_emotions=[EmotionScore(**emotion) for emotion in top_emotions],
            tags=tags,
            created_at=entry_data["created_at"],
            entry_id=entry_id,
            sentiment=legacy_sentiment  # Legacy compatibility for frontend
        )
        
    except Exception as e:
        logging.error(f"Error processing reflection: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to process reflection: {str(e)}")

@router.get("/entries")
async def get_entries(
    limit: int = 30,
    authorization: Optional[str] = Header(None)
):
    """
    Fetch recent reflections for the authenticated user from Supabase.
    
    Requires authentication via Authorization header: Bearer <token>
    
    Args:
        limit: Maximum number of entries to return (default: 30)
        authorization: Authorization header with Bearer token
    
    Returns:
        JSON with entries array and count
    """
    try:
        # Get authenticated user_id from token
        user_id = get_user_id_from_token(authorization)
        
        # Extract token from authorization header for RLS
        token = None
        if authorization:
            parts = authorization.split()
            if len(parts) == 2 and parts[0].lower() == "bearer":
                token = parts[1]
        
        logging.info(f"Fetching {limit} recent entries for user {user_id}")
        entries = await supabase_client.get_user_entries(user_id=user_id, limit=limit, access_token=token)
        logging.info(f"Retrieved {len(entries)} entries for user {user_id}")
        return {"entries": entries, "count": len(entries)}
        
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Error fetching entries: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch entries: {str(e)}")
