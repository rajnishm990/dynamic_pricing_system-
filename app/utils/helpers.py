from datetime import datetime
from typing import List


def calculate_average(prices: List[float]) -> float:
    """Calculate average of a list of prices"""
    if not prices:
        return 0.0
    return sum(prices) / len(prices)


def round_price(price: float, decimals: int = 2) -> float:
    """Round price to specified decimal places"""
    return round(price, decimals)


def format_currency(price: float, currency: str = "INR") -> str:
    """Format price as currency string"""
    return f"{currency} {price:.2f}"


def is_cache_valid(cached_time: datetime, expiry_minutes: int) -> bool:
    """Check if cached data is still valid"""
    now = datetime.utcnow()
    difference = (now - cached_time).total_seconds() / 60
    return difference < expiry_minutes


def normalize_value(value: float, min_val: float, max_val: float) -> float:
    """
    Normalize a value between 0 and 1
    Useful for scaling different factors to same range
    """
    if max_val == min_val:
        return 0.5
    return (value - min_val) / (max_val - min_val)


def categorize_temperature(temp: float) -> str:
    """Categorize temperature into human-readable ranges"""
    if temp < 10:
        return "Cold"
    elif temp < 20:
        return "Cool"
    elif temp < 30:
        return "Warm"
    else:
        return "Hot"