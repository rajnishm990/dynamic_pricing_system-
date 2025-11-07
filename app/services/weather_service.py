import httpx
from datetime import datetime, timedelta , timezone
from typing import Optional, Dict
from sqlalchemy.orm import Session
from app.core.config import settings
from app.models.database import WeatherCache


class WeatherService:
    """ 
    Service for fetching and caching weather data 
     
    """
    def __init__(self):
        self.api_key = settings.OPENWEATHER_API_KEY 
        self.base_url = settings.OPENWEATHER_BASE_URL 
    
    async def get_weather(self, city:str  , db:Optional[Session]=None) -> Dict:
        """ 
        fetched weahter data for a city
        checks from cache first , if cache miss go for API 
        """
        if db:
            cached = self._get_from_cache(city , db)
            if cached:
                return cached
        
        #fetch from API
        weather_data = self._fetch_from_api(city)

        #save to cache
        if db and weather_data:
            self._save_to_cache(city, weather_data, db)
        
        return weather_data
    
    def _get_from_cache(self, city:str, db:Session ) -> Optional[Dict]:

        cache_expiry = datetime.now(timezone.utc) - timedelta(
            minutes=settings.WEATHER_CACHE_MINUTES
            )
        
        cached_weather = db.query(WeatherCache).filter(
            WeatherCache.city == city,
            WeatherCache.fetched_at > cache_expiry
        ).first()
        
        if cached_weather:
            return {
                "city": city,
                "temperature": cached_weather.temperature,
                "condition": cached_weather.condition,
                "cached": True
            }
        
        return None
    
    async def _fetch_from_api(self, city:str) -> Dict:

        if not self.api_key or self.api_key == "demo":
            # Return mock data for demo
            return {
                "city": city,
                "temperature": 28,
                "condition": "Sunny",
                "note": "Using mock data. Set OPENWEATHER_API_KEY for real data."
            }
        
        try:
            async with httpx.AsyncClient() as client:
                response=await client.get(
                    f"{self.base_url}/weather",
                    params={
                        "q": city,
                        "appid": self.api_key,
                        "units": "metric"
                    },
                    timeout=10.0
                )
                if response.status_code == 200:
                    data = response.json()
                    return {
                        "city": city,
                        "temperature": data["main"]["temp"],
                        "condition": data["weather"][0]["main"],
                        "cached": False
                    }
                else:
                    # Fallback to mock data on error
                    return {
                        "city": city,
                        "temperature": 25,
                        "condition": "Clear",
                        "note": "API error, using fallback data"
                    }
        except Exception as e:
            print(f"Error fetching weather: {e}")
            return {
                "city": city,
                "temperature": 25,
                "condition": "Clear",
                "note": "Error fetching data"
            }
        
    def _save_to_cache(self, city: str, weather_data: Dict, db: Session):
        
        try:
            cache_entry = WeatherCache(
                city=city,
                temperature=weather_data.get("temperature", 25),
                condition=weather_data.get("condition", "Clear"),
                raw_data=weather_data
            )
            db.add(cache_entry)
            db.commit()
        except Exception as e:
            print(f"Error saving to cache: {e}")
            db.rollback()


# Global instance
weather_service = WeatherService()