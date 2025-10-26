from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from services.reflection_ai import ReflectionAI
from services.sentiment import SentimentAnalyzer
from services.tagging import ThemeExtractor
from supabase_client import SupabaseClient
from datetime import datetime
import logging

router = APIRouter()

# Initialize services
reflection_ai = ReflectionAI()
sentiment_analyzer = SentimentAnalyzer()
theme_extractor = ThemeExtractor()
supabase_client = SupabaseClient()

class ReflectionRequest(BaseModel):
    text: str
    user_id: Optional[str] = "default_user"

class ReflectionResponse(BaseModel):
    summary: str
    sentiment: str
    tags: List[str]
    created_at: str
    entry_id: str

@router.post("/reflect", response_model=ReflectionResponse)
async def process_reflection(request: ReflectionRequest):
    """
    Process a user's reflection text through AI analysis pipeline
    
    Input: {"text": "Got a lot done in Devfolio but skipped gym again."}
    Process:
    1. Run sentiment → positive | neutral | negative
    2. Run reflection → short empathetic summary + actionable nudge
    3. Run tag extraction → list of themes (coding, gym, discipline)
    4. Insert record into Supabase table `entries`
    5. Return full JSON
    """
    try:
        # Validate input
        if not request.text.strip():
            raise HTTPException(status_code=400, detail="Reflection text cannot be empty")
        
        logging.info(f"Processing reflection: {request.text[:50]}...")
        
        # 1. Sentiment Analysis
        sentiment = await sentiment_analyzer.analyze(request.text)
        logging.info(f"Sentiment detected: {sentiment}")
        
        # 2. Generate empathetic summary
        summary = await reflection_ai.generate_summary(request.text, sentiment)
        logging.info(f"Summary generated: {summary[:50]}...")
        
        # 3. Extract themes/tags
        tags = await theme_extractor.extract_themes(request.text)
        logging.info(f"Tags extracted: {tags}")
        
        # 4. Save to database
        entry_data = {
            "user_id": request.user_id,
            "text": request.text,
            "ai_summary": summary,
            "sentiment": sentiment,
            "tags": tags,
            "created_at": datetime.utcnow().isoformat()
        }
        
        entry_id = await supabase_client.save_reflection(entry_data)
        logging.info(f"Entry saved with ID: {entry_id}")
        
        return ReflectionResponse(
            summary=summary,
            sentiment=sentiment,
            tags=tags,
            created_at=entry_data["created_at"],
            entry_id=entry_id
        )
        
    except Exception as e:
        logging.error(f"Error processing reflection: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to process reflection: {str(e)}")

@router.get("/entries")
async def get_entries(limit: int = 30):
    """
    Fetch recent reflections from Supabase (limit 30).
    Return JSON list.
    """
    try:
        logging.info(f"Fetching {limit} recent entries")
        entries = await supabase_client.get_recent_entries(limit)
        logging.info(f"Retrieved {len(entries)} entries")
        return {"entries": entries, "count": len(entries)}
        
    except Exception as e:
        logging.error(f"Error fetching entries: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch entries: {str(e)}")
