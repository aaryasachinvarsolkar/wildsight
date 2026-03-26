from typing import Dict, Any, List
import joblib
import os
import numpy as np
from pathlib import Path
from app.models.schemas import RiskAssessment, EnvironmentalData

class RiskEstimator:
    def __init__(self):
        self.model = None
        self._load_model()

    def _load_model(self):
        try:
            base_dir = Path(__file__).resolve().parent.parent.parent
            model_path = base_dir / "models" / "risk_model.pkl"
            if model_path.exists():
                self.model = joblib.load(model_path)
                print(f"ML ENGINE: Loaded Risk/Population Model from {model_path}")
        except Exception as e:
            print(f"ML ENGINE ERROR: Could not load model pkl: {e}")

    def estimate_risk(self, env: EnvironmentalData, meta: Dict[str, Any]) -> RiskAssessment:
        """
        Uses the loaded scikit-learn model to perform real-time risk assessment.
        Falls back to heuristics if model is unavailable.
        """
        if not self.model:
            return self._heuristic_fallback(env)

        try:
            # 1. Prepare Feature Vector
            # Features: ['ndvi', 'evi', 'ndwi', 'temperature', 'rainfall', 'hdi', 'nightlights', 'is_mammal', 'is_bird', 'is_reptile', 'is_amphibian', 'is_fish', 'is_plant', 'is_insect', 'is_marine', 'is_fungi']
            
            kingdom = meta.get("kingdom", "").lower()
            cls = meta.get("class", "").lower()
            
            features = {
                'ndvi': env.ndvi,
                'evi': getattr(env, 'evi', 0.5),
                'ndwi': getattr(env, 'ndwi', 0.0),
                'temperature': env.temperature_celsius,
                'rainfall': env.rainfall_forecast_mm,
                'hdi': env.human_development_index,
                'nightlights': getattr(env, 'nightlights', 5.0),
                'is_mammal': 1.0 if cls == 'mammalia' else 0.0,
                'is_bird': 1.0 if cls == 'aves' else 0.0,
                'is_reptile': 1.0 if cls == 'reptilia' else 0.0,
                'is_amphibian': 1.0 if cls == 'amphibia' else 0.0,
                'is_fish': 1.0 if 'actinopterygii' in cls or 'chondrichthyes' in cls else 0.0,
                'is_plant': 1.0 if 'plantae' in kingdom else 0.0,
                'is_insect': 1.0 if cls == 'insecta' else 0.0,
                'is_marine': 1.0 if 'marine' in meta.get('order', '').lower() else 0.0,
                'is_fungi': 1.0 if 'fungi' in kingdom else 0.0
            }
            
            # Form the list in correct order
            X = [features[col] for col in self.model['feature_cols']]
            X_arr = np.array([X])
            
            # 2. Prediction
            # Classifier returns risk category (e.g. 0=Low, 1=Medium, 2=High)
            pred_class = self.model['classifier'].predict(X_arr)[0]
            # Probabilities for a score
            probs = self.model['classifier'].predict_proba(X_arr)[0]
            score = float(np.sum(probs * np.array([0.2, 0.5, 0.9]))) # Weighted average score
            
            # Regressor for population density (optional context)
            pop_density = self.model['regressor'].predict(X_arr)[0]
            
            # Map Stressor (Heuristic lookup based on highest threat feature)
            stressors = {"fire": env.fire_radiative_power/20, "drought": 1-(env.rainfall_forecast_mm/1000), "encroachment": env.human_development_index}
            primary = max(stressors, key=stressors.get)

            return RiskAssessment(
                risk_score=round(score, 2),
                primary_stressor=primary,
                anomaly_detected=(score > 0.75),
                details={
                    "model_confidence": round(float(np.max(probs)), 2),
                    "predicted_density": round(float(pop_density), 2),
                    "is_ml_powered": True
                }
            )
        except Exception as e:
            print(f"ML INFERENCE ERROR: {e}")
            return self._heuristic_fallback(env)

    def _heuristic_fallback(self, env: EnvironmentalData) -> RiskAssessment:
        # Simplified version of the previous formula
        score = 0.5
        if env.fire_radiative_power > 0: score += 0.2
        if env.human_development_index > 0.6: score += 0.1
        return RiskAssessment(risk_score=min(1.0, score), primary_stressor="climate_volatility", anomaly_detected=False, details={"is_ml_powered": False})

risk_estimator = RiskEstimator()
