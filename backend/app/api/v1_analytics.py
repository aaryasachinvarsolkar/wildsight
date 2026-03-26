from fastapi import APIRouter, HTTPException, Depends, Query
from typing import List
import os
from datetime import datetime, timedelta
from sqlmodel import select, Session
from app.models.db import get_session, RiskPrediction, EnvironmentalHistory
from app.services.environmental import environmental_service
from app.services.taxonomy import taxonomy_service
from app.services.population import population_service
from app.services.analysis.risk import risk_estimator
from app.services.analysis.prediction import prediction_service
from app.services.conservation import conservation_service
from app.services.report import report_service
from app.models.schemas import ZoneAnalysis, RiskAssessment, EnvironmentalData, BiometricFeature, Prescription
from fastapi.responses import FileResponse
import h3

router = APIRouter()

@router.get("/zones/risk/{z}/{x}/{y}") 
async def get_risk_tiles(z: int, x: int, y: int):
    return {"message": "MVT Tile Placeholder", "coords": [z, x, y]}

@router.get("/species/{species_name}/occupancy")
def get_species_occupancy(species_name: str, lat: float, lon: float):
    env_data = environmental_service.get_environmental_data(lat, lon)
    key, name, meta = taxonomy_service.resolve_name(species_name)
    ideal = taxonomy_service.species_db.get(name.lower(), {}).get("ideal_env")
    probability = prediction_service.predict_habitat_occupancy(env_data, ideal)
    return {
        "species": name,
        "location": {"lat": lat, "lon": lon},
        "occupancy_probability": probability,
        "environmental_factors": env_data
    }

@router.get("/prescriptions/{h3_index}")
def get_prescriptions(h3_index: str, species: str = "unknown", session: Session = Depends(get_session)):
    try:
        try: lat, lon = h3.cell_to_latlng(h3_index)
        except: lat, lon = h3.h3_to_geo(h3_index)
            
        env_data = environmental_service.get_environmental_data(lat, lon)
        key, name, meta = taxonomy_service.resolve_name(species)
        pop_data = population_service.get_population_data(name, key=key)
        
        # Sensitivities
        sensitivities = {"fire": 0.5, "rainfall": 0.5, "temp": 0.5, "hdi": 0.5, "ndvi": 0.5}
        risk = risk_estimator.estimate_risk(env_data, sensitivities)
        
        actions = conservation_service.recommend_actions(risk, h3_index, name, pop_data['estimated_population'], env_data)
        prediction = prediction_service.predict_future_outlook(pop_data['population_history'], env_data)
        
        return {
            "zone": h3_index,
            "risk_assessment": {
                "risk_level": "High" if risk.risk_score > 0.6 else "Low",
                "risk_score": risk.risk_score,
                "confidence": 0.95,
                "explanation": actions[0].description if actions else "N/A",
                "details": risk.details
            },
            "recommended_actions": [a.dict() for a in actions],
            "meta": {"source": "computed", "created_at": datetime.utcnow(), "future_outlook": prediction}
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/report/{species_name}")
def get_detailed_report(species_name: str, lat: float = None, lon: float = None, zone_id: str = Query(None)):
    try:
        key, name, meta = taxonomy_service.resolve_name(species_name)
        pop_data = population_service.get_population_data(name, key)
        
        if lat is None or lon is None:
            if zone_id:
                try: lat, lon = h3.cell_to_latlng(zone_id)
                except: pass
            if (lat is None or lon is None) and pop_data['checkpoints']:
                lat, lon = pop_data['checkpoints'][0]['lat'], pop_data['checkpoints'][0]['lon']
            if lat is None or lon is None: lat, lon = 20.5937, 78.9629

        env_data = environmental_service.get_environmental_data(lat, lon)
        sensitivities = {"fire": 0.5, "rainfall": 0.5, "temp": 0.5, "hdi": 0.5, "ndvi": 0.5}
        risk = risk_estimator.estimate_risk(env_data, sensitivities)
        
        actions = conservation_service.recommend_actions(risk, env_data.h3_index, name, pop_data['estimated_population'], env_data)
        prediction = prediction_service.predict_future_outlook(pop_data['population_history'], env_data)

        env_context = {
            "avg_ndvi": env_data.ndvi,
            "avg_temp": env_data.temperature_celsius,
            "avg_rain": env_data.rainfall_forecast_mm,
            "hdi": env_data.human_development_index,
            "risk_score": risk.risk_score,
            "future_outlook": prediction
        }

        report_text = report_service.generate_llm_report(
            species_name=name,
            species_data={"status": "Vulnerable", "estimated_population": pop_data["estimated_population"], "biological_traits": meta, "population_history": pop_data["population_history"]},
            env_context=env_context,
            conservation_plan=[a.dict() for a in actions]
        )
        
        return {"report": report_text}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/report/download/{species_name}")
def download_report_pdf(species_name: str, payload: dict):
    report_text = payload.get("report_text", "")
    pdf_path = report_service.generate_pdf_report(species_name, report_text)
    if not pdf_path or not os.path.exists(pdf_path):
        raise HTTPException(status_code=500, detail="Failed to generate PDF")
    return FileResponse(path=pdf_path, filename=os.path.basename(pdf_path), media_type="application/pdf")
