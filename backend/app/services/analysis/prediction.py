from typing import List, Dict, Any
import numpy as np
import random
from datetime import datetime
from app.models.schemas import EnvironmentalData

class PredictionService:
    def predict_future_outlook(self, history: List[Dict], env: EnvironmentalData) -> Dict[str, Any]:
        """
        Predicts future population trend using history and climate outlook.
        No longer uses fake on-the-fly training.
        """
        if not history or len(history) < 3:
            return {"verdict": "Stable (Assumed)", "endangerment_probability": 0.2, "primary_driver": "Insufficient data to project trend.", "projected_decline_rate": 0.0}
            
        # Linear Trend analysis on actual population counts
        y = np.array([p.get("count", 0) for p in history])
        x = np.arange(len(y))
        slope, intercept = np.polyfit(x, y, 1)
        
        # Calculate Percentage Decline per Year
        current_pop = y[-1] if y[-1] > 0 else 1
        pct_change = slope / current_pop
        
        verdict = "Stable"
        prob = 0.1
        driver = "Population trend is stable."
        
        if pct_change < -0.05:
            verdict, prob, driver = "Vulnerable", 0.6, "Rapid population decline detected."
            if pct_change < -0.15: verdict, prob, driver = "Critically Endangered", 0.9, "Catastrophic population collapse imminent."
        
        # Environmental stressors from current data
        if getattr(env, 'ndvi', 0.5) < 0.3:
            prob = min(1.0, prob + 0.2)
            driver += " Compounded by habitat degradation."

        return {
            "verdict": verdict,
            "endangerment_probability": round(prob, 2),
            "primary_driver": driver,
            "projected_decline_rate": round(pct_change * 100, 1)
        }

    def predict_habitat_occupancy(self, env: EnvironmentalData, ideal_config: Dict = None) -> float:
        """
        Predicts suitability using environmental vectors.
        Uses a rule-based expert system based on biological niche rather than a fake Random Forest.
        """
        if not ideal_config: # Generalist
            ideal_config = {'ndvi': 0.5, 'temp': 25.0, 'rainfall': 1000.0, 'hdi': 0.4}
            
        ndvi_diff = abs(getattr(env, 'ndvi', 0.5) - ideal_config.get('ndvi', 0.5))
        temp_diff = abs(getattr(env, 'temperature_celsius', 25.0) - ideal_config.get('temp', 25.0)) / 10.0
        hdi_penalty = max(0, getattr(env, 'human_development_index', 0.4) - ideal_config.get('hdi', 0.4))
        
        suitability = 1.0 - (0.4 * ndvi_diff + 0.3 * temp_diff + 0.3 * hdi_penalty)
        return round(float(max(0.0, min(1.0, suitability))), 2)

prediction_service = PredictionService()
