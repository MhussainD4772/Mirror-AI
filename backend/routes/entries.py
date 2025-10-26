from fastapi import APIRouter, HTTPException
from typing import List, Optional
from supabase_client import SupabaseClient
from datetime import datetime, timedelta
import logging

router = APIRouter()
supabase_client = SupabaseClient()

@router.get("/entries")
async def get_entries(
    user_id: str = "default_user",
    limit: int = 50,
    days_back: int = 30
):
    """
    Get user's reflection entries with optional filtering
    """
    try:
        entries = await supabase_client.get_user_entries(
            user_id=user_id,
            limit=limit,
            days_back=days_back
        )
        return {"entries": entries, "count": len(entries)}
    except Exception as e:
        logging.error(f"Error fetching entries: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch entries: {str(e)}")

@router.get("/entries/stats")
async def get_entry_stats(user_id: str = "default_user"):
    """
    Get aggregated statistics for user's entries
    """
    try:
        stats = await supabase_client.get_user_stats(user_id)
        return stats
    except Exception as e:
        logging.error(f"Error fetching stats: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch stats: {str(e)}")

@router.get("/entries/trends")
async def get_trends(
    user_id: str = "default_user",
    period: str = "week"  # week, month, year
):
    """
    Get trend analysis for user's reflections
    """
    try:
        trends = await supabase_client.get_trends(user_id, period)
        return trends
    except Exception as e:
        logging.error(f"Error fetching trends: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch trends: {str(e)}")

@router.delete("/entries/{entry_id}")
async def delete_entry(entry_id: str):
    """
    Delete a specific reflection entry
    """
    try:
        success = await supabase_client.delete_reflection(entry_id)
        if not success:
            raise HTTPException(status_code=404, detail="Entry not found")
        return {"message": "Entry deleted successfully"}
    except Exception as e:
        logging.error(f"Error deleting entry: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to delete entry: {str(e)}")
