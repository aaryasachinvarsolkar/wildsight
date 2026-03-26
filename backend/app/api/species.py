from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import JSONResponse
import traceback
import time
from typing import Dict, Any, List
import math
import numpy as np
import h3

from app.services.taxonomy import taxonomy_service
from app.services.environmental import environmental_service
from app.services.population import population_service
from app.services.analysis.risk import risk_estimator
from app.services.analysis.prediction import prediction_service
from app.services.conservation import conservation_service
from app.models.db import Session, engine, EnvironmentalHistory, select

router = APIRouter()

def sanitize_response(obj):
    if isinstance(obj, float):
        if math.isnan(obj) or math.isinf(obj): return 0.0
        return obj
    if isinstance(obj, dict): return {k: sanitize_response(v) for k, v in obj.items()}
    if isinstance(obj, list): return [sanitize_response(v) for v in obj]
    if isinstance(obj, np.generic):
        if np.isnan(obj) or np.isinf(obj): return 0.0
        return obj.item()
    return obj

@router.get("/{species_name}")
def get_species_intelligence(
    species_name: str, 
    lat: float = None,
    lon: float = None,
    zone_id: str = Query(None),
    location: str = Query(None)
):
    start_time = time.time()
    try:
        # 0. Handle Geocoding for Location names
        if location and (lat is None or lon is None):
            try:
                import requests
                geo_res = requests.get("https://nominatim.openstreetmap.org/search", params={"q": location, "format": "json", "limit": 1}, headers={"User-Agent": "WildSight-AI/1.0"}, timeout=3.0)
                if geo_res.status_code == 200 and geo_res.json():
                    lat = float(geo_res.json()[0]["lat"])
                    lon = float(geo_res.json()[0]["lon"])
            except Exception as e:
                print(f"Geocoding error: {e}")
        # 1. Resolve Taxonomy
        key, name, meta = taxonomy_service.resolve_name(species_name)
        if not key:
            raise HTTPException(status_code=404, detail=f"Species '{species_name}' not found.")

        # 2. Get Population Data (Real Census & GBIF Trends)
        pop_data = population_service.get_population_data(name, key=key)
        
        # 3. Handle Location
        if lat is None or lon is None:
            if zone_id:
                try:
                    lat, lon = h3.cell_to_latlng(zone_id)
                except: pass
            if (lat is None or lon is None) and pop_data['checkpoints']:
                lat, lon = pop_data['checkpoints'][0]['lat'], pop_data['checkpoints'][0]['lon']
            if lat is None or lon is None: lat, lon = 20.5937, 78.9629 # Default India

        # 4. Get Current Environmental Data (Sentinel + Open-Meteo)
        env_data = environmental_service.get_environmental_data(lat, lon)
        
        # 5. Assess Risk (ML Powered)
        risk = risk_estimator.estimate_risk(env_data, meta)
        
        # 5.5 If population is missing, use ML Regressor to predict density
        current_pop = pop_data['estimated_population']
        if current_pop <= 0 and risk_estimator.model:
             # Re-run a small inference for population if not already in risk details
             predicted_pop = risk.details.get("predicted_density", 0)
             # Scale density to a readable number (e.g. per district)
             current_pop = int(predicted_pop * 1000) if predicted_pop > 0 else 150
             pop_data['estimated_population'] = current_pop
        
        # 6. Predict Future Outlook
        prediction = prediction_service.predict_future_outlook(pop_data['population_history'], env_data)
        occupancy = prediction_service.predict_habitat_occupancy(env_data, taxonomy_service.species_db.get(name.lower(), {}).get("ideal_env"))

        # 7. Get Conservation Actions
        actions = conservation_service.recommend_actions(risk, env_data.h3_index, name, pop_data['estimated_population'], env_data)

        # 8. Fetch REAL Historical Trends from DB (Populated by environmental_service)
        with Session(engine) as session:
            history = session.exec(select(EnvironmentalHistory).where(EnvironmentalHistory.h3_index == env_data.h3_index).order_by(EnvironmentalHistory.timestamp)).all()
        
        # Format history for frontend graphs
        # We need daily (last 5 entries for mock "last 5 days") and yearly (since 2021)
        # Actually, let's use the real history we just fetched.
        
        years = [str(h.timestamp.year) for h in history if h.timestamp.month == 8]
        yearly_ndvi = [h.ndvi for h in history if h.timestamp.month == 8]
        yearly_evi = [h.evi for h in history if h.timestamp.month == 8]
        yearly_ndwi = [h.ndwi for h in history if h.timestamp.month == 8]
        yearly_temp = [h.temperature for h in history if h.timestamp.month == 8]
        yearly_rain = [h.rainfall for h in history if h.timestamp.month == 8]
        yearly_frp = [h.frp for h in history if h.timestamp.month == 8]

        # 9. Build Response
        response = {
            "species": {
                "species_name": name,
                "scientific_name": meta.get("scientificName"),
                "status": pop_data.get("status", "Vulnerable"),
                "estimated_population": pop_data["estimated_population"],
                "population_history": pop_data["population_history"],
                "checkpoints": pop_data["checkpoints"],
                "biological_traits": meta,
                "analysis": {
                    "vegetation": {"ndvi": yearly_ndvi[-5:], "evi": yearly_evi[-5:], "ndwi": yearly_ndwi[-5:]},
                    "climate": {"temp": yearly_temp[-5:], "rain": yearly_rain[-5:]},
                    "disturbance": {"frp": yearly_frp[-5:], "nightlight": [h.nightlights for h in history][-5:]}
                },
                "years": [p["year"] for p in pop_data["population_history"]],
                "years_forecast": [2027, 2028, 2029, 2030, 2031], # Forecast stays simple for now
                "days_vegetation": ["Day 1", "Day 2", "Day 3", "Day 4", "Today"],
                "years_disturbance": years[-5:]
            },
            "environment_context": {
                "avg_ndvi": env_data.ndvi,
                "avg_temp": env_data.temperature_celsius,
                "avg_rain": env_data.rainfall_forecast_mm,
                "hdi": env_data.human_development_index,
                "risk_score": risk.risk_score,
                "future_outlook": prediction,
                "is_cached": env_data.is_cached
            },
            "occupancy_probability": occupancy,
            "conservation_plan": [a.dict() for a in actions]
        }

        return sanitize_response(response)
    except Exception as e:
        print(f"Error: {e}")
        traceback.print_exc()
        return JSONResponse(status_code=500, content={"detail": str(e)})

taxonomy_service._load_data() # Ensure data loaded
