from sqlalchemy import Column, Integer, Float, String, DateTime, JSON
from datetime import datetime , timezone
from app.db.database import Base

def utc_now():
    """Return timezone aware time."""
    return datetime.now(timezone.utc)


class PricingHistory(Base):
    """
    Store historical pricing decisions for analysis , Can help us track pricing changes 
    """
    __tablename__ = "pricing_history"
    
    id = Column(Integer, primary_key=True, index=True)
    menu_item_id = Column(Integer, index=True)
    current_price = Column(Float)
    recommended_price = Column(Float)
    competitor_avg_price = Column(Float)
    weather_condition = Column(String)
    temperature = Column(Float)
    event_count = Column(Integer)
    reasoning = Column(String)
    created_at = Column(DateTime, default=utc_now)


class WeatherCache(Base):
    """
    Cache weather data to reduce API calls
    Weather doesn't change every minute, so we can cache it
    """
    __tablename__ = "weather_cache"
    
    id = Column(Integer, primary_key=True, index=True)
    city = Column(String, index=True)
    temperature = Column(Float)
    condition = Column(String)
    raw_data = Column(JSON)
    fetched_at = Column(DateTime, default=utc_now)


class EventCache(Base):
    """
    Cache event data to reduce API calls
    Events don't change frequently within the same day
    """
    __tablename__ = "event_cache"
    
    id = Column(Integer, primary_key=True, index=True)
    location = Column(String, index=True)
    event_name = Column(String)
    popularity = Column(String)
    distance_km = Column(Float)
    event_date = Column(DateTime)
    raw_data = Column(JSON)
    fetched_at = Column(DateTime, default=utc_now)


class CompetitorPrice(Base):
    """
    Track competitor pricing over time
    Helps identify trends and patterns
    """
    __tablename__ = "competitor_prices"
    
    id = Column(Integer, primary_key=True, index=True)
    menu_item_id = Column(Integer, index=True)
    competitor_name = Column(String)
    price = Column(Float)
    recorded_at = Column(DateTime, default=utc_now)