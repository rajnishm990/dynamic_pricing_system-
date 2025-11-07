from fastapi import APIRouter , HTTPException , Depends 
from sqlalchemy.orm import Session 
from app.schemas.pricing import PricingRequest , PricingResponse 
from app.services.pricing_engine import pricing_engine 
from app.db.database import get_db 
from app.models.database import PricingHistory
from datetime import datetime

router = APIRouter(prefix="/api/pricing", tags=["Pricing"])

@router.post("/suggest", response_model=PricingResponse)
async def suggest_price(request: PricingRequest , db:Session =Depends(get_db)):
    """
    Generate AI-powered pricing suggestions for menu items
    
    This endpoint analyzes internal factors (competitor prices) and external factors
    (weather, events) to recommend optimal pricing.
    
    **Parameters:**
    - menu_item_id: Unique identifier for the menu item
    - current_price: Current price of the item
    - competitor_prices: List of competitor prices for similar items
    - weather: Weather conditions (temperature, condition)
    - events: List of nearby events affecting demand
    
    **Returns:**
    - recommended_price: AI-suggested optimal price
    - factors: Weights used in calculation
    - reasoning: Human-readable explanation
    """
    try:
        response = pricing_engine.suggest_price(request)

        try:
            avg_competitor =(sum(request.competitor_prices)/ len(request.competitor_prices) if request.competitor_prices else request.current_price)
            
            history_entry = PricingHistory(
                menu_item_id=request.menu_item_id,
                current_price=request.current_price,
                recommended_price=response.recommended_price,
                competitor_avg_price=avg_competitor,
                weather_condition=request.weather.condition,
                temperature=request.weather.temperature,
                event_count=len(request.events),
                reasoning=response.reasoning,
                created_at=datetime.utcnow()
            )
            
            db.add(history_entry)
            db.commit() 
        except Exception as db_error:
            # Don't fail the request if database save fails
            print(f"Error saving to database: {db_error}")
            db.rollback()
        
        return response
    
    except Exception as e:
        raise HTTPException(status_code=500,detail=f"Error calculating price: {str(e)}")


@router.get("/history/{menu_item_id}")
async def get_pricing_history(menu_item_id: int,limit: int = 10,db: Session = Depends(get_db)):
    """
    Get historical pricing data for a menu item
    Useful for analyzing pricing trends over time
    """
    try:
        history = db.query(PricingHistory).filter(PricingHistory.menu_item_id == menu_item_id).order_by(PricingHistory.created_at.desc()
        ).limit(limit).all()
        
        return {
            "menu_item_id": menu_item_id,
            "history": [
                {
                    "date": h.created_at.isoformat(),
                    "current_price": h.current_price,
                    "recommended_price": h.recommended_price,
                    "competitor_avg": h.competitor_avg_price,
                    "reasoning": h.reasoning
                }
                for h in history
            ]
        }
    
    except Exception as e:
        raise HTTPException(status_code=500,detail=f"Error fetching history: {str(e)}")