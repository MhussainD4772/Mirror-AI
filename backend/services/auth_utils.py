import os
import logging
from fastapi import HTTPException, Header
from typing import Optional
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv('../.env')

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_ANON_KEY = os.getenv("SUPABASE_ANON_KEY")


def get_user_id_from_token(authorization: Optional[str] = Header(None)) -> str:
    """
    Validate Supabase auth token and extract user_id.
    
    Args:
        authorization: Authorization header value (e.g., "Bearer <token>")
    
    Returns:
        user_id (str): The authenticated user's ID
    
    Raises:
        HTTPException: If token is missing or invalid
    """
    if not authorization:
        raise HTTPException(
            status_code=401,
            detail="Authorization header is required"
        )
    
    # Extract token from "Bearer <token>" format
    parts = authorization.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        raise HTTPException(
            status_code=401,
            detail="Invalid authorization header format. Expected: Bearer <token>"
        )
    
    token = parts[1]
    
    if not SUPABASE_URL or not SUPABASE_ANON_KEY:
        logging.error("Supabase credentials not configured")
        raise HTTPException(
            status_code=500,
            detail="Authentication service not configured"
        )
    
    try:
        # Create a Supabase client to validate the token
        supabase_client: Client = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)
        
        # Validate token and get user - use jwt parameter
        user_response = supabase_client.auth.get_user(jwt=token)
        
        if not user_response or not user_response.user:
            raise HTTPException(
                status_code=401,
                detail="Invalid or expired token"
            )
        
        user_id = str(user_response.user.id)
        logging.info(f"Authenticated user: {user_id}")
        return user_id
        
    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except Exception as e:
        logging.error(f"Token validation error: {str(e)}")
        raise HTTPException(
            status_code=401,
            detail=f"Authentication failed: {str(e)}"
        )

