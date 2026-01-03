from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
from routes.reflect import router as reflect_router
from routes.entries import router as entries_router
import os
from dotenv import load_dotenv
import logging

# Load environment variables
load_dotenv('../.env')

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Mirror AI - Reflection System",
    description="AI-powered personal reflection and emotional analysis system",
    version="1.0.0"
)

# CORS middleware for frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # Local development
        "https://mirror-ai.vercel.app",  # Vercel deployment
        "https://*.vercel.app",  # Any Vercel subdomain
        "https://mirror-ai-frontend.vercel.app",  # Alternative Vercel URL
        "*"  # Allow all origins for production (can be restricted later)
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

# Include routers
app.include_router(reflect_router, tags=["reflection"])
app.include_router(entries_router, tags=["entries"])

@app.get("/")
async def root():
    return {
        "message": "Mirror AI - Reflection System API", 
        "status": "running",
        "version": "1.0.0",
        "endpoints": {
            "reflect": "POST /reflect",
            "entries": "GET /entries"
        }
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy", 
        "service": "mirror-ai-backend",
        "environment": os.getenv("NODE_ENV", "development")
    }

if __name__ == "__main__":
    logger.info("Starting Mirror AI Backend Server...")
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
