from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.services.event_service import event_service
from app.db.database import get_db

router = APIRouter(prefix="/api/events", tags=["Events"])


@router.get("/{location}")
async def get_events(
    location: str,
    radius_km: float = Query(5.0, ge=1.0, le=50.0, description="Search radius in kilometers"),
    db: Session = Depends(get_db)
):
    """
    Fetch nearby events for a location
    
    This is a helper endpoint for getting event information
    that can be used in pricing calculations.
    
    **Parameters:**
    - location: City or area name
    - radius_km: Search radius in kilometers (1-50)
    
    **Returns:**
    - List of events with name, popularity, and distance
    """
    events = await event_service.get_events(location, radius_km, db)
    return {
        "location": location,
        "radius_km": radius_km,
        "events": events
    }