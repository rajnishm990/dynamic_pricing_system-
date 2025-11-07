import httpx
from datetime import datetime, timedelta
from typing import Optional, List, Dict
from sqlalchemy.orm import Session
from app.core.config import settings
from app.models.database import EventCache


class EventService:
    """
    Service for fetching and caching event data
    Integrates with Ticketmaster API
    """
    
    def __init__(self):
        self.api_key = settings.TICKETMASTER_API_KEY
        self.base_url = settings.TICKETMASTER_BASE_URL
    
    async def get_events(self, location: str, radius_km: float = 5.0, 
                         db: Optional[Session] = None) -> List[Dict]:
        """
        Get nearby events for a location
        """
        
        if db:
            cached = self._get_from_cache(location, db)
            if cached:
                return cached
        
        events = await self._fetch_from_api(location, radius_km)
        
        
        if db and events:
            self._save_to_cache(location, events, db)
        
        return events
    
    def _get_from_cache(self, location: str, db: Session) -> Optional[List[Dict]]:
        """Check if we have recent cached event data"""
        cache_expiry = datetime.utcnow() - timedelta(
            hours=settings.EVENT_CACHE_HOURS
        )
        
        cached_events = db.query(EventCache).filter(
            EventCache.location == location,
            EventCache.fetched_at > cache_expiry
        ).all()
        
        if cached_events:
            return [
                {
                    "name": event.event_name,
                    "popularity": event.popularity,
                    "distance_km": event.distance_km,
                    "cached": True
                }
                for event in cached_events
            ]
        
        return None
    
    async def _fetch_from_api(self, location: str, radius_km: float) -> List[Dict]:
        """
        Fetch events from Ticketmaster API
        In production, use real API key and handle errors properly
        """
        if not self.api_key or self.api_key == "demo_key":
            # Return mock data for demo
            return [
                {
                    "name": "Food Festival",
                    "popularity": "High",
                    "distance_km": 2.5,
                    "note": "Using mock data. Set TICKETMASTER_API_KEY for real data."
                },
                {
                    "name": "Music Concert",
                    "popularity": "Medium",
                    "distance_km": 4.0,
                    "note": "Mock event data"
                }
            ]
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/events.json",
                    params={
                        "apikey": self.api_key,
                        "city": location,
                        "radius": radius_km,
                        "unit": "km"
                    },
                    timeout=10.0
                )
                
                if response.status_code == 200:
                    data = response.json()
                    events = []
                    
                    for event in data.get("_embedded", {}).get("events", [])[:5]:
                        events.append({
                            "name": event.get("name", "Unknown Event"),
                            "popularity": self._determine_popularity(event),
                            "distance_km": radius_km / 2,  # Approximate
                            "cached": False
                        })
                    
                    return events
                else:
                    return []
        
        except Exception as e:
            print(f"Error fetching events: {e}")
            return []
    
    def _determine_popularity(self, event_data: Dict) -> str:
        """
        Determine event popularity based on available data
        This is a simplified heuristic
        """
        # In production, use ticket sales, venue size, etc.
        classifications = event_data.get("classifications", [])
        if classifications:
            genre = classifications[0].get("genre", {}).get("name", "").lower()
            if "festival" in genre or "concert" in genre:
                return "High"
        
        return "Medium"
    
    def _save_to_cache(self, location: str, events: List[Dict], db: Session):
        """Save events to cache"""
        try:
            for event in events:
                cache_entry = EventCache(
                    location=location,
                    event_name=event.get("name", "Unknown"),
                    popularity=event.get("popularity", "Medium"),
                    distance_km=event.get("distance_km", 5.0),
                    raw_data=event
                )
                db.add(cache_entry)
            db.commit()
        except Exception as e:
            print(f"Error saving events to cache: {e}")
            db.rollback()

event_service = EventService()
