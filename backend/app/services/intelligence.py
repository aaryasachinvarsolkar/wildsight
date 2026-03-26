from typing import List, Dict, Any
from app.services.analysis.risk import risk_estimator
from app.services.analysis.prediction import prediction_service
from app.services.conservation import conservation_service
from app.models.schemas import RiskAssessment, Prescription, EnvironmentalData

class AnomalyDetector:
    def detect_anomaly(self, history: List[EnvironmentalData]) -> bool:
        if not history or len(history) < 2: return False
        # Basic rule-based anomaly (delta ndvi or fire)
        curr, prev = history[-1], history[-2]
        if getattr(curr, "ndvi", 0.5) < getattr(prev, "ndvi", 0.5) - 0.2: return True
        if getattr(curr, "fire_radiative_power", 0.0) > 10.0: return True
        return False

# Wrappers for existing code
risk_estimator = risk_estimator
prediction_engine = conservation_service 
habitat_model = prediction_service 
climate_predictor = prediction_service 
trend_analyzer = prediction_service # Note: I'll need to add a few methods for compatibility

# Add compatibility methods if needed (dummy to avoid crashing)
class HabitatModelWrapper:
    def predict_occupancy(self, species, env, ideal_config=None):
        return prediction_service.predict_habitat_occupancy(env, ideal_config)

habitat_model = HabitatModelWrapper()

class PrescriptionEngineWrapper:
    def recommend_actions(self, risk, zone_id, species_name, population_count=None, species_data=None, env_data=None):
        pop = population_count or (species_data.get("estimated_population") if species_data else 1000)
        return conservation_service.recommend_actions(risk, zone_id, species_name, pop, env_data)

prescription_engine = PrescriptionEngineWrapper()

class ClimatePredictorWrapper:
    def predict_future_scenario(self, env, stressor="unknown"):
        # Dummy forecast for compatibility
        import datetime
        years = [datetime.datetime.now().year + i for i in range(1, 6)]
        return {"years": years, "temp": [getattr(env, "temperature_celsius", 25.0) + i*0.5 for i in range(5)], "rain": [getattr(env, "rainfall_forecast_mm", 1000.0) - i*50 for i in range(5)]}

climate_predictor = ClimatePredictorWrapper()

class TrendAnalyzerWrapper:
    def simulate_daily_vegetation(self, env, days=5):
        nv = getattr(env, "ndvi", 0.5)
        return {"ndvi": [nv for _ in range(5)], "evi": [nv*0.9 for _ in range(5)], "ndwi": [0.2 for _ in range(5)], "labels": [f"Day {i}" for i in range(5)]}
    def simulate_yearly_disturbance(self, env, years=5):
        fr = getattr(env, "fire_radiative_power", 0.0)
        return {"frp": [fr for _ in range(5)], "nightlights": [getattr(env, "human_development_index", 0.4)*10 for _ in range(5)], "labels": [str(2021+i) for i in range(5)]}

trend_analyzer = TrendAnalyzerWrapper()
anomaly_detector = AnomalyDetector()
