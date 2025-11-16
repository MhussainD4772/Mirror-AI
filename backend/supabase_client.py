import os
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from supabase import create_client, Client
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv('../.env')

class SupabaseClient:
    """
    Client for handling all Supabase database operations.
    Table structure now includes emotions data:
    entries (
        id, user_id, text, ai_summary, sentiment, dominant_emotion,
        emotions, tags, created_at
    )
    """
    
    def __init__(self):
        self.url = os.getenv("SUPABASE_URL")
        self.key = os.getenv("SUPABASE_ANON_KEY")
        
        if not self.url or not self.key:
            raise Exception("Supabase credentials not found. Please set SUPABASE_URL and SUPABASE_ANON_KEY in your .env file.")
        
        self.client: Client = create_client(self.url, self.key)
        logging.info("Supabase client initialized successfully")
    
    async def save_reflection(self, entry_data: Dict[str, Any]) -> str:
        """
        Insert record into Supabase table `entries`
        Columns include: text, ai_summary, sentiment (legacy), dominant_emotion,
        emotions (jsonb), tags, created_at
        """
        try:
            # Prepare data for Supabase with correct column names
            data = {
                "user_id": entry_data.get("user_id"),
                "text": entry_data["text"],
                "ai_summary": entry_data["ai_summary"],
                "sentiment": entry_data["sentiment"],
                "dominant_emotion": entry_data.get("dominant_emotion"),
                "emotions": entry_data.get("emotions"),
                "tags": entry_data["tags"],
                "created_at": entry_data["created_at"]
            }
            
            logging.info(f"Saving to Supabase: {data}")
            result = self.client.table("entries").insert(data).execute()
            
            if result.data:
                entry_id = str(result.data[0]["id"])
                logging.info(f"Entry saved successfully with ID: {entry_id}")
                return entry_id
            else:
                raise Exception("Failed to save reflection - no data returned")
                
        except Exception as e:
            logging.error(f"Error saving reflection: {str(e)}")
            raise e
    
    async def get_recent_entries(self, limit: int = 30) -> List[Dict[str, Any]]:
        """
        Fetch recent reflections from Supabase (limit 30).
        Return JSON list.
        """
        try:
            logging.info(f"Fetching {limit} recent entries from Supabase")
            result = (
                self.client.table("entries")
                .select("*")
                .order("created_at", desc=True)
                .limit(limit)
                .execute()
            )
            
            entries = self._normalize_entries(result.data or [])
            logging.info(f"Retrieved {len(entries)} entries from Supabase")
            return entries
            
        except Exception as e:
            logging.error(f"Error fetching entries: {str(e)}")
            raise e
    
    async def get_reflection(self, entry_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a specific reflection entry by ID
        """
        try:
            result = self.client.table("entries").select("*").eq("id", entry_id).execute()
            
            if result.data:
                entries = self._normalize_entries(result.data)
                return entries[0] if entries else None
            return None
            
        except Exception as e:
            logging.error(f"Error fetching reflection: {str(e)}")
            raise e
    
    async def get_user_entries(
        self, 
        user_id: str, 
        limit: int = 50, 
        days_back: int = 30
    ) -> List[Dict[str, Any]]:
        """
        Get user's reflection entries with optional filtering
        """
        try:
            # Calculate date filter
            start_date = datetime.now() - timedelta(days=days_back)
            
            result = (
                self.client.table("entries")
                .select("*")
                .eq("user_id", user_id)
                .gte("created_at", start_date.isoformat())
                .order("created_at", desc=True)
                .limit(limit)
                .execute()
            )
            
            return self._normalize_entries(result.data or [])
            
        except Exception as e:
            logging.error(f"Error fetching user entries: {str(e)}")
            raise e
    
    async def get_user_stats(self, user_id: str) -> Dict[str, Any]:
        """
        Get aggregated statistics for user's entries
        """
        try:
            # Get all entries for stats calculation
            result = (
                self.client.table("entries")
                .select("*")
                .eq("user_id", user_id)
                .execute()
            )
            
            entries = self._normalize_entries(result.data or [])
            
            if not entries:
                return {
                    "total_entries": 0,
                    "sentiment_distribution": {},
                    "top_tags": [],
                    "avg_entries_per_week": 0,
                    "streak_days": 0
                }
            
            # Calculate stats
            total_entries = len(entries)
            
            # Sentiment distribution
            sentiment_counts = {}
            all_tags = []
            
            for entry in entries:
                dominant_emotion = entry.get("dominant_emotion") or entry.get("sentiment", "neutral")
                sentiment_counts[dominant_emotion] = sentiment_counts.get(dominant_emotion, 0) + 1
                
                tags = entry.get("tags", [])
                if isinstance(tags, str):
                    tags = json.loads(tags) if tags else []
                all_tags.extend(tags)
            
            # Top tags
            tag_counts = {}
            for tag in all_tags:
                tag_counts[tag] = tag_counts.get(tag, 0) + 1
            
            top_tags = sorted(tag_counts.items(), key=lambda x: x[1], reverse=True)[:10]
            top_tags = [tag[0] for tag in top_tags]
            
            # Calculate streak (simplified)
            streak_days = self._calculate_streak(entries)
            
            return {
                "total_entries": total_entries,
                "sentiment_distribution": sentiment_counts,
                "top_tags": top_tags,
                "avg_entries_per_week": total_entries / max(1, len(entries) // 7),
                "streak_days": streak_days
            }
            
        except Exception as e:
            logging.error(f"Error calculating user stats: {str(e)}")
            raise e
    
    async def get_trends(self, user_id: str, period: str = "week") -> Dict[str, Any]:
        """
        Get trend analysis for user's reflections
        """
        try:
            # Get entries for the specified period
            days_back = {"week": 7, "month": 30, "year": 365}.get(period, 7)
            start_date = datetime.now() - timedelta(days=days_back)
            
            result = (
                self.client.table("entries")
                .select("*")
                .eq("user_id", user_id)
                .gte("created_at", start_date.isoformat())
                .order("created_at", desc=False)
                .execute()
            )
            
            entries = result.data or []
            
            # Process trends
            mood_trend = []
            tag_frequency = {}
            
            for entry in entries:
                created_at = entry.get("created_at", "")
                if created_at:
                    date_str = created_at.split("T")[0]
                    dominant_emotion = entry.get("dominant_emotion") or entry.get("sentiment", "neutral")
                    mood_trend.append({
                        "date": date_str,
                        "sentiment": dominant_emotion
                    })
                
                tags = entry.get("tags", [])
                if isinstance(tags, str):
                    tags = json.loads(tags) if tags else []
                
                for tag in tags:
                    tag_frequency[tag] = tag_frequency.get(tag, 0) + 1
            
            # Generate insights
            insights = self._generate_insights(entries, tag_frequency)
            
            return {
                "mood_trend": mood_trend,
                "tag_frequency": tag_frequency,
                "insights": insights
            }
            
        except Exception as e:
            logging.error(f"Error calculating trends: {str(e)}")
            raise e
    
    async def delete_reflection(self, entry_id: str) -> bool:
        """
        Delete a specific reflection entry
        """
        try:
            result = self.client.table("entries").delete().eq("id", entry_id).execute()
            return len(result.data) > 0
            
        except Exception as e:
            logging.error(f"Error deleting reflection: {str(e)}")
            raise e
    
    def _normalize_entries(self, entries: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Ensure JSON/text columns are consistently typed when fetched from Supabase.
        """
        normalized_entries: List[Dict[str, Any]] = []
        for entry in entries:
            normalized_entry = dict(entry)

            tags = normalized_entry.get("tags", [])
            if isinstance(tags, str):
                try:
                    normalized_entry["tags"] = json.loads(tags) if tags else []
                except json.JSONDecodeError:
                    normalized_entry["tags"] = [tag.strip() for tag in tags.split(",") if tag.strip()]

            emotions = normalized_entry.get("emotions")
            if isinstance(emotions, str):
                try:
                    normalized_entry["emotions"] = json.loads(emotions) if emotions else {}
                except json.JSONDecodeError:
                    normalized_entry["emotions"] = {}

            top_emotions = normalized_entry.get("top_emotions")
            if isinstance(top_emotions, str):
                try:
                    normalized_entry["top_emotions"] = json.loads(top_emotions) if top_emotions else []
                except json.JSONDecodeError:
                    normalized_entry["top_emotions"] = []
            elif top_emotions is None:
                normalized_entry["top_emotions"] = []

            if normalized_entry.get("emotions"):
                sorted_emotions = sorted(
                    normalized_entry["emotions"].items(),
                    key=lambda item: item[1],
                    reverse=True,
                )
                normalized_entry["top_emotions"] = [
                    {"label": label, "score": float(score)}
                    for label, score in sorted_emotions[:3]
                ]

            if not normalized_entry.get("dominant_emotion"):
                dominant = None
                if normalized_entry.get("top_emotions"):
                    dominant = normalized_entry["top_emotions"][0]["label"]
                dominant = dominant or normalized_entry.get("sentiment", "neutral")
                normalized_entry["dominant_emotion"] = dominant

            normalized_entries.append(normalized_entry)

        return normalized_entries

    def _calculate_streak(self, entries: List[Dict[str, Any]]) -> int:
        """
        Calculate consecutive days with entries
        """
        if not entries:
            return 0
        
        # Sort entries by date
        sorted_entries = sorted(entries, key=lambda x: x.get("created_at", ""), reverse=True)
        
        streak = 0
        current_date = datetime.now().date()
        
        for entry in sorted_entries:
            entry_date_str = entry.get("created_at", "").split("T")[0]
            entry_date = datetime.fromisoformat(entry_date_str).date()
            
            if entry_date == current_date:
                streak += 1
                current_date -= timedelta(days=1)
            elif entry_date < current_date:
                break
        
        return streak
    
    def _generate_insights(self, entries: List[Dict[str, Any]], tag_frequency: Dict[str, int]) -> List[str]:
        """
        Generate AI-like insights from the data
        """
        insights = []
        
        if not entries:
            return ["Start your reflection journey today!"]
        
        # Emotion insights
        emotions = [entry.get("dominant_emotion") or entry.get("sentiment", "neutral") for entry in entries]
        if emotions:
            counts: Dict[str, int] = {}
            for emotion in emotions:
                counts[emotion] = counts.get(emotion, 0) + 1
            top_emotion = max(counts.items(), key=lambda item: item[1])
            insights.append(f"You've been feeling a lot of {top_emotion[0]} lately. Notice what sparks this emotion.")
        
        # Tag insights
        if tag_frequency:
            top_tag = max(tag_frequency.items(), key=lambda x: x[1])
            insights.append(f"'{top_tag[0]}' appears {top_tag[1]} times - it's clearly important to you.")
        
        # Frequency insights
        if len(entries) >= 7:
            insights.append("Great consistency! You're building a valuable habit.")
        elif len(entries) < 3:
            insights.append("Consider reflecting more regularly to build self-awareness.")
        
        return insights[:3]  # Limit to 3 insights
