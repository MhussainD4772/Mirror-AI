from fastapi import APIRouter, HTTPException, Header
from typing import Optional
from supabase_client import SupabaseClient
from services.auth_utils import get_user_id_from_token
from datetime import datetime, timedelta
import logging

router = APIRouter()
supabase_client = SupabaseClient()

@router.get("/entries/stats")
async def get_entry_stats(
    authorization: Optional[str] = Header(None)
):
    """
    Get aggregated statistics for the authenticated user's entries
    
    Requires authentication via Authorization header: Bearer <token>
    """
    try:
        user_id = get_user_id_from_token(authorization)
        # Extract token for RLS
        token = None
        if authorization:
            parts = authorization.split()
            if len(parts) == 2 and parts[0].lower() == "bearer":
                token = parts[1]
        stats = await supabase_client.get_user_stats(user_id, access_token=token)
        return stats
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Error fetching stats: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch stats: {str(e)}")

@router.get("/entries/trends")
async def get_trends(
    period: str = "week",  # week, month, year
    authorization: Optional[str] = Header(None)
):
    """
    Get trend analysis for the authenticated user's reflections
    
    Requires authentication via Authorization header: Bearer <token>
    """
    try:
        user_id = get_user_id_from_token(authorization)
        # Extract token for RLS
        token = None
        if authorization:
            parts = authorization.split()
            if len(parts) == 2 and parts[0].lower() == "bearer":
                token = parts[1]
        trends = await supabase_client.get_trends(user_id, period, access_token=token)
        return trends
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Error fetching trends: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch trends: {str(e)}")

@router.delete("/entries/{entry_id}")
async def delete_entry(
    entry_id: str,
    authorization: Optional[str] = Header(None)
):
    """
    Delete a specific reflection entry (only if owned by authenticated user)
    
    Requires authentication via Authorization header: Bearer <token>
    """
    try:
        user_id = get_user_id_from_token(authorization)
        success = await supabase_client.delete_reflection(entry_id, user_id)
        if not success:
            raise HTTPException(status_code=404, detail="Entry not found or access denied")
        return {"message": "Entry deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Error deleting entry: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to delete entry: {str(e)}")
