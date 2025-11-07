from pydantic import BaseModel, Field
from typing import List


class WeatherData(BaseModel):
    """Schema for weather information"""
    temperature: float = Field(..., description="Temperature in Celsius")
    condition: str = Field(..., description="Weather condition (e.g., Sunny, Rainy)")
    
    class Config:
        json_schema_extra = {
            "example": {
                "temperature": 28,
                "condition": "Sunny"
            }
        }


class EventData(BaseModel):
    """Schema for event information"""
    name: str = Field(..., description="Name of the event")
    popularity: str = Field(..., description="Event popularity: Low, Medium, High")
    distance_km: float = Field(..., description="Distance from resturant in kilometers")
    
    class Config:
        json_schema_extra = {
            "example": {
                "name": "Food Festival",
                "popularity": "High",
                "distance_km": 2.5
            }
        }


class PricingRequest(BaseModel):
    """Request schema for pricing suggestions"""
    menu_item_id: int = Field(..., description="Unique identifier for menu item")
    current_price: float = Field(..., gt=0, description="Current price of the item")
    competitor_prices: List[float] = Field(..., description="List of competitor prices")
    weather: WeatherData
    events: List[EventData] = Field(default=[], description="List of nearby events")
    
    class Config:
        json_schema_extra = {
            "example": {
                "menu_item_id": 123,
                "current_price": 250,
                "competitor_prices": [240, 260, 245],
                "weather": {
                    "temperature": 32,
                    "condition": "Sunny"
                },
                "events": [
                    {
                        "name": "Food Festival",
                        "popularity": "High",
                        "distance_km": 2.5
                    }
                ]
            }
        }


class FactorWeights(BaseModel):
    """Schema for factor weights in pricing calculation"""
    internal_weight: float = Field(..., description="Weight given to internal factors")
    external_weight: float = Field(..., description="Weight given to external factors")


class PricingResponse(BaseModel):
    """Response schema for pricing suggestions"""
    menu_item_id: int
    recommended_price: float = Field(..., description="AI-suggested price")
    factors: FactorWeights
    reasoning: str = Field(..., description="Explanation of pricing decision")
    
    class Config:
        json_schema_extra = {
            "example": {
                "menu_item_id": 123,
                "recommended_price": 268,
                "factors": {
                    "internal_weight": 0.6,
                    "external_weight": 0.4
                },
                "reasoning": "Price adjustment recommended due to: competitors are pricing higher, favorable weather (Sunny, 32°C), nearby events (Food Festival) increasing demand."
            }
        }