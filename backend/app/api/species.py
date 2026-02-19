from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import JSONResponse
import traceback
import time
from typing import Dict, Any, List
from app.services.biometric import biometric_service
from app.services.geospatial import geospatial_service
from app.services.intelligence import prescription_engine, habitat_model, climate_predictor, trend_analyzer
from app.models.schemas import RiskAssessment

router = APIRouter()

@router.get("/test/hello")
async def hello():
    return {"message": "hello"}

import math
import numpy as np

def sanitize_response(obj):
    if isinstance(obj, float):
        if math.isnan(obj) or math.isinf(obj):
            return 0.0
        return obj
    if isinstance(obj, dict):
        return {k: sanitize_response(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [sanitize_response(v) for v in obj]
    if isinstance(obj, np.generic): # Handle numpy scalars
        if np.isnan(obj) or np.isinf(obj):
            return 0.0
        return obj.item()
    return obj

@router.get("/{species_name}")
async def get_species_intelligence(
    species_name: str, 
    lat: float = None,
    lon: float = None,
    zone_id: str = Query(None, description="H3 Index for specific habitat filtering") # [Phase 3]
):
    start_time = time.time()
    try:
        # 1. Get Species Bio-Data (Checkpoints, Traits, etc.)
        # Now passing zone_id to filter 5-day pulse history
        print(f"DEBUG: Starting Biometric Fetch for {species_name}")
        bio_start = time.time()
        bio_data = biometric_service.get_species_data(species_name, zone_id=zone_id)
        print(f"DEBUG: Biometric Fetch took {time.time() - bio_start:.2f}s")
        
        if not bio_data or not bio_data.get("species_name"):
            # Species not found in "Real Life" (GBIF)
            print(f"ERROR: Species '{species_name}' could not be resolved or fetched.")
            raise HTTPException(status_code=404, detail=f"Species '{species_name}' not found in biodiversity records. Try a more common name.")

        checkpoints = bio_data.get("checkpoints", [])
        
        # Fallback if no location provided: Use Zone ID if available, else first checkpoint
        if lat is None or lon is None:
            if zone_id:
                try:
                    import h3
                    try:
                        lat, lon = h3.h3_to_geo(zone_id)
                    except AttributeError:
                        lat, lon = h3.cell_to_latlng(zone_id)
                    print(f"DEBUG: H3 Decoded to {lat}, {lon} for zone analysis")
                except Exception as e:
                    print(f"H3 Decode Failed: {e}")
            
            if (lat is None or lon is None) and checkpoints:
                lat = checkpoints[0]['lat']
                lon = checkpoints[0]['lon']
            
            # Absolute default
            if lat is None or lon is None:
                lat, lon = 20.5937, 78.9629 # Center of India default
        
        # 2. Get Environment Data for current location
        t_env_start = time.time()
        env_data = geospatial_service.get_environmental_data(lat, lon)
        print(f"DEBUG: Env Fetch took {time.time() - t_env_start:.2f}s")
        
        # 3. Assess Risk dynamically using ML Engine (Species-Aware)
        t_risk_start = time.time()
        from app.services.intelligence import risk_estimator
        sensitivities = bio_data.get("sensitivities", {})
        
        risk = risk_estimator.estimate_risk(env_data, sensitivities)
        risk_score = risk.risk_score
        primary_stressor = risk.primary_stressor
        print(f"DEBUG: Risk Eval took {time.time() - t_risk_start:.2f}s")

        # 4. Generate Explainable Data ( The "Evidence" )
        # Use the determined stressor to generate realistic history/forecasts
        
        # [Updated Logic] Split into specific timeframes as requested
        # Vegetation: Last 5 Days (Daily)
        veg_data = trend_analyzer.simulate_daily_vegetation(env_data, days=5)
        
        # Disturbance: Last 5 Years (Yearly)
        dist_data = trend_analyzer.simulate_yearly_disturbance(env_data, years=5)
        
        # Forecast Data (Climate) - Next 5 Years
        forecast_data = climate_predictor.predict_future_scenario(env_data, stressor=primary_stressor)
        
        # 5. Get Prescriptions ( The "Solution" )
        t_pre_start = time.time()
        actions = prescription_engine.recommend_actions(risk, zone_id or "national", species_name, species_data=bio_data, env_data=env_data)
        print(f"DEBUG: Prescription took {time.time() - t_pre_start:.2f}s")
        
        # 6. Occupancy Probability
        t_oc_start = time.time()
        ideal_env = bio_data.get("ideal_env")
        occupancy = habitat_model.predict_occupancy(species_name, env_data, ideal_config=ideal_env)
        print(f"DEBUG: Occupancy took {time.time() - t_oc_start:.2f}s")

        # 7. Construct Final Response aligned with Frontend
        years_forecast = forecast_data["years"]

        bio_data["analysis"] = {
            "vegetation": {
                "ndvi": veg_data["ndvi"],
                "evi": veg_data["evi"],
                "ndwi": veg_data["ndwi"]
            },
            "climate": {
                "temp": forecast_data["temp"],
                "rain": forecast_data["rain"]
            },
            "disturbance": {
                "frp": dist_data["frp"],
                "nightlight": dist_data["nightlights"]
            }
        }
        # Add timeline metadata [Updated for diverse graphs]
        bio_data["days_vegetation"] = veg_data["labels"] # e.g. ["Jan 01", "Jan 02"]
        bio_data["years_disturbance"] = dist_data["labels"] # e.g. ["2021", "2022"]
        bio_data["years_forecast"] = years_forecast # e.g. [2026, 2027]
        
        # Fallback for old graph component if needed (though we will update frontend)
        bio_data["years_history"] = dist_data["labels"] 
        
        # Fixed 2021-2025 years for the Vulnerability Graph
        bio_data["years"] = [p["year"] for p in bio_data.get("population_history", [])]

        # [Refactor] Removed Duplicate PulseLog fetching.
        # It is now handled inside biometric_service.get_species_data(..., zone_id)
        
        response_data = {
            "species": bio_data,
            "environment_context": {
                "avg_ndvi": env_data.ndvi,
                "avg_temp": env_data.temperature_celsius,
                "avg_rain": env_data.rainfall_forecast_mm,
                "hdi": env_data.human_development_index,
                "risk_score": risk_score
            },
            "occupancy_probability": occupancy,
            "conservation_plan": [action.dict() for action in actions]
        }
        
        print(f"DEBUG: Total Intelligence Prep took {time.time() - start_time:.2f}s")
        return sanitize_response(response_data)
    except HTTPException as he:
        # Re-raise HTTP exceptions so they propagate as intended (e.g. 404)
        raise he
    except Exception as e:
        print(f"Server Error: {e}")
        traceback.print_exc()
        return JSONResponse(
            status_code=500,
            content={"detail": str(e), "traceback": traceback.format_exc()}
        )
