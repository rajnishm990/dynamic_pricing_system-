import math 
from typing import List 
from app.schemas.pricing import PricingRequest, PricingResponse, FactorWeights, WeatherData, EventData
from app.core.config import settings 

class PricingEnging:
    """ 
    Core Pricing logic using weighed factors . Basic as of now  
    Potential Update: Enhance using ML models like linear regression or Neural Net 

    """

    def __init__(self):
        self.internal_weight = settings.INTERNAL_WEIGHT 
        self.external_weight = settings.EXTERNAL_WEIGHT  

    def calculate_competitor_factor(self, current_price : float , competitor_prices : List[float]) -> float:
        """  
        How our price compare to competitiors 
        Returns: Multiplying factor
        """
        if not competitor_prices:
            return 1.0 
        avg_competitor_price = sum(competitor_prices) / len(competitor_prices)
        
        # If we're cheaper, we can increase price
        # If we're expensive, we should decrease
        price_ratio = avg_competitor_price / current_price
        
        # Normalize to a factor between 0.9 and 1.15
        factor = 0.95 + (price_ratio - 1) * 0.3
        return max(0.9, min(1.15, factor))
    
    def calculate(self , weather: WeatherData) -> float :
        """ 
        calculate demand based on weather conditions
        Good Weather means higher demand for outings 
        """
        base_factor = 1.0 

        if 20 <= weather.temperature <= 30:
            #perfect
            base_factor+=0.8
        elif weather.temperature > 35:
            # Too hot, 
            base_factor -= 0.05
        elif weather.temperature < 10:
            # Cold weather
            base_factor -= 0.03
        
        #condition impact 
        condition = weather.condition.lower()
        if any(word in condition for word in ["sunny", "clear", "fair"]):
            base_factor += 0.05
        elif any(word in condition for word in ["rain", "storm", "snow"]):
            base_factor -= 0.08
        
        return base_factor 

    def calculate_event_factor(self, events: List[EventData]) -> float:
        """
        Calculate demand increase based on nearby events
        Events bring more customers = higher prices
        """
        if not events:
            return 1.0
        
        total_impact = 0
        
        for event in events:
            # Popularity impact
            popularity_multiplier = {
                "low": 0.02,
                "medium": 0.05,
                "high": 0.10
            }
            pop_impact = popularity_multiplier.get(event.popularity.lower(), 0.03)
            
            # Distance impact (closer events have more impact)
            # Using exponential decay: impact decreases with distance
            distance_factor = math.exp(-0.3 * event.distance_km)
            
            event_impact = pop_impact * distance_factor
            total_impact += event_impact
        
        return 1.0 + total_impact
    
    def suggest_price(self, request: PricingRequest) -> PricingResponse:
        """
        Main pricing algorithm that combines all factors
        """
        # Calculate individual factors
        competitor_factor = self.calculate_competitor_factor(
            request.current_price, 
            request.competitor_prices
        )
        weather_factor = self.calculate_weather_factor(request.weather)
        event_factor = self.calculate_event_factor(request.events)
        
        # Combine external factors
        external_factor = (weather_factor + event_factor - 1.0)
        
        # Apply weights to internal and external factors
        price_adjustment = (
            self.internal_weight * (competitor_factor - 1.0) +
            self.external_weight * external_factor
        )
        
        # Calculate recommended price
        recommended_price = request.current_price * (1 + price_adjustment)
        
        # Round to nearest reasonable value
        recommended_price = round(recommended_price, 2)
        
        # Generate reasoning text
        reasoning = self._generate_reasoning(
            request, competitor_factor, weather_factor, event_factor
        )
        
        return PricingResponse(
            menu_item_id=request.menu_item_id,
            recommended_price=recommended_price,
            factors=FactorWeights(
                internal_weight=self.internal_weight,
                external_weight=self.external_weight
            ),
            reasoning=reasoning
        )
    
    def _generate_reasoning(self, request: PricingRequest, 
                           comp_factor: float, weather_factor: float, 
                           event_factor: float) -> str:
        """Generate human-readable reasoning for the price suggestion"""
        reasons = []
        
        # Competitor analysis
        if request.competitor_prices:
            avg_comp = sum(request.competitor_prices) / len(request.competitor_prices)
            if request.current_price < avg_comp:
                reasons.append("competitors are pricing higher")
            elif request.current_price > avg_comp:
                reasons.append("competitive pressure suggests lower pricing")
        
        # Weather analysis
        if weather_factor > 1.03:
            reasons.append(
                f"favorable weather ({request.weather.condition}, "
                f"{request.weather.temperature}°C)"
            )
        elif weather_factor < 0.97:
            reasons.append("unfavorable weather conditions")
        
        # Events analysis
        if event_factor > 1.02 and request.events:
            event_names = [e.name for e in request.events[:2]]
            reasons.append(
                f"nearby events ({', '.join(event_names)}) increasing demand"
            )
        
        if not reasons:
            return "Market conditions are stable. Current pricing is optimal."
        
        return "Price adjustment recommended due to: " + ", ".join(reasons) + "."


# Create global instance
pricing_engine = PricingEngine()


