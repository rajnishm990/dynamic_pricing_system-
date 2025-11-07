from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.services.weather_service import weather_service
from app.db.database import get_db

router = APIRouter(prefix="/api/weather", tags=["Weather"])


@router.get("/{city}")
async def get_weather(city: str, db: Session = Depends(get_db)):
    """
    Fetch real-time weather data for a city
    
    This is a helper endpoint for getting weather information
    that can be used in pricing calculations.
    
    **Parameters:**
    - city: Name of the city
    
    **Returns:**
    - temperature: Current temperature in Celsius
    - condition: Weather condition (Sunny, Rainy, etc.)
    - cached: Whether data came from cache
    """
    weather_data = await weather_service.get_weather(city, db)
    return weather_data