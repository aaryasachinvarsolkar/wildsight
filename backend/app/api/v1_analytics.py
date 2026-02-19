from fastapi import APIRouter, HTTPException, Depends, Query
from typing import List
import random
from datetime import datetime, timedelta
from sqlmodel import select, Session
from app.models.db import get_session, RiskPrediction
from app.services.geospatial import geospatial_service
from app.services.intelligence import anomaly_detector, habitat_model, prescription_engine, risk_estimator, AnomalyDetector, HabitatModel, PrescriptionEngine

# ... (rest of imports)


from app.models.schemas import ZoneAnalysis, RiskAssessment, EnvironmentalData, BiometricFeature, Prescription
from fastapi.responses import FileResponse
from app.services.report import report_service
from app.services.biometric import biometric_service
from app.services.intelligence import trend_analyzer, climate_predictor, prescription_engine, risk_estimator, ecosystem_predictor
import os

router = APIRouter()

@router.get("/zones/risk/{z}/{x}/{y}") 
# Note: Ideally response_class=Response for binary MVT, but mocked as dict/json for now or using custom response
async def get_risk_tiles(z: int, x: int, y: int):
    """
    Returns Mapbox Vector Tiles (MVT) for risk zones.
    """
    tile_data = geospatial_service.get_tile(z, x, y)
    # In a real app, return Response(content=tile_data, media_type="application/x-protobuf")
    return {"message": "MVT Tile Placeholder", "coords": [z, x, y]}

@router.get("/species/{species_name}/occupancy")
async def get_species_occupancy(species_name: str, lat: float, lon: float):
    """
    Returns predicted occupancy probability.
    """
    env_data = geospatial_service.get_environmental_data(lat, lon)
    probability = habitat_model.predict_occupancy(species_name, env_data)
    return {
        "species": species_name,
        "location": {"lat": lat, "lon": lon},
        "occupancy_probability": probability,
        "environmental_factors": env_data
    }

@router.post("/predict/anomaly")
async def predict_anomaly(history: List[EnvironmentalData]):
    """
    Analyzes a time-series of environmental data to detect anomalies.
    """
    is_anomaly = anomaly_detector.detect_anomaly(history)
    return {"anomaly_detected": is_anomaly}

@router.get("/prescriptions/{h3_index}")
async def get_prescriptions(h3_index: str, species: str = "unknown", count: int = None, session: Session = Depends(get_session)):
    """
    Returns prescriptive conservation actions using the Trained ML Model.
    Enforces a 5-day cache policy for reproducibility and scalability.
    """
    # 0. Check Database Cache (Pulse Logic)
    CURRENT_MODEL_VERSION = "3.0.0-ECO"
    try:
        statement = select(RiskPrediction).where(
            RiskPrediction.species_name == species,
            RiskPrediction.h3_index == h3_index
        ).order_by(RiskPrediction.created_at.desc())
        
        existing = session.exec(statement).first()
        
        # 5-Day Validity Check + Model Version Check
        if existing:
            age = datetime.utcnow() - existing.created_at
            # Invalidate if too old OR if model version suggests legacy data
            if age < timedelta(days=5) and existing.model_version == CURRENT_MODEL_VERSION:
                # Return Cached only if valid AND fresh
                return {
                    "zone": h3_index,
                    "risk_assessment": {
                        "risk_level": existing.risk_level,
                        "risk_score": existing.features_snapshot.get("risk", 0.5), # Add this for frontend NaN fix
                        "confidence": existing.confidence,
                        "explanation": existing.explanation,
                        "details": existing.features_snapshot
                    },
                    "recommended_actions": [Prescription(
                        action_type="Based on Risk Level", # Placeholder action
                        priority=existing.risk_level.lower(),
                        target_zone_h3=h3_index,
                        estimated_cost=0, 
                        expected_outcome="Cached Prediction",
                        description=existing.explanation
                    )],
                    "meta": {
                        "source": "cached", 
                        "age_hours": age.total_seconds() / 3600,
                        "model_version": existing.model_version,
                        "created_at": existing.created_at
                    }
                }
    except Exception as e:
        print(f"DB Read Error: {e}")

    # 1. Environment & Risk Simulation (If not cached)
    # Note: In a real flow, we would need lat/lon here to fetch weather.
    # Since H3 is provided, we can find center.
    try:
        import h3
        try:
            lat, lon = h3.h3_to_geo(h3_index)
        except AttributeError:
             # Support for h3-py v4+
            lat, lon = h3.cell_to_latlng(h3_index)
            
        env_data = geospatial_service.get_environmental_data(lat, lon)
        
        # 2. Risk Heuristic & Inference (New ML Engine)
        # 2. Risk Heuristic & Inference (New ML Engine)
        # Fetch Biological Sensitivity Profile
        from app.services.biometric import biometric_service
        species_data = biometric_service.get_species_data(species)
        sensitivities = species_data.get("sensitivities", {})
        
        # Calculate Risk using Math Engine
        risk = risk_estimator.estimate_risk(env_data, sensitivities)
        
        # Extract results
        risk_score = risk.risk_score
        primary_story = risk.primary_stressor
        
        # Call New Engine
        actions = prescription_engine.recommend_actions(risk, h3_index, species_name=species, env_data=env_data, species_data=species_data)
        
        # [Phase 3] Predict Ecosystem Context
        ecosystem_ctx = ecosystem_predictor.predict(env_data, species_data.get("population_history", []), species_data)
        
        # Take the top action or default
        best_action = actions[0] if actions else Prescription(
            action_type="Monitor", 
            priority="low", 
            description="No specific action recommended.", 
            target_zone_h3=h3_index, 
            estimated_cost=0, 
            expected_outcome="Monitoring"
        )
        
        # 3. Save to Database (Persistence)
        new_pred = RiskPrediction(
            species_name=species,
            h3_index=h3_index,
            risk_level="High" if risk_score > 0.6 else "Low",
            confidence=0.95,
            explanation=best_action.description, # Save the full report
            model_version="3.0.0-ECO",
            prediction_source="computed",
            created_at=datetime.utcnow(),
            features_snapshot={
                "risk": risk_score, 
                "stressor": primary_story,
                "predicted_count": ecosystem_ctx["predicted_count"],
                "predicted_status": ecosystem_ctx["predicted_status"],
                "habitat_quality": ecosystem_ctx["habitat_quality_score"]
            }
        )
        session.add(new_pred)
        session.commit()
    
        # 4. Construct Response
        return {
            "zone": h3_index,
            "risk_assessment": {
                "risk_level": "High" if risk_score > 0.6 else "Low",
                "risk_score": float(risk_score), # Add this for frontend NaN fix
                "confidence": 0.95,
                "explanation": best_action.description,
                "details": {
                    "risk": risk_score,
                    "predicted_count": ecosystem_ctx["predicted_count"],
                    "predicted_status": ecosystem_ctx["predicted_status"],
                    "habitat_quality": ecosystem_ctx["habitat_quality_score"],
                    "urban_pressure": ecosystem_ctx["urban_pressure"]
                }
            },
            "recommended_actions": [best_action],
             "meta": {
                 "source": "computed",
                 "model_version": "3.0.0-ECO",
                 "created_at": datetime.utcnow()
             }
        }
    except Exception as e:
        print(f"Compute Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/report/{species_name}")
async def get_detailed_report(species_name: str, lat: float = None, lon: float = None, zone_id: str = Query(None)):
    """
    Generates a detailed AI report for a species based on its current context.
    """
    try:
        # 1. Fetch current data context
        bio_data = biometric_service.get_species_data(species_name)
        if not bio_data:
            raise HTTPException(status_code=404, detail="Species not found")
        
        if lat is None or lon is None:
             if zone_id:
                 try:
                     import h3
                     try:
                        lat, lon = h3.h3_to_geo(zone_id)
                     except AttributeError:
                        lat, lon = h3.cell_to_latlng(zone_id)
                 except Exception:
                     pass

             if lat is None or lon is None:
                 checkpoints = bio_data.get("checkpoints", [])
                 if checkpoints:
                     lat, lon = checkpoints[0]["lat"], checkpoints[0]["lon"]
                 else:
                     lat, lon = 20.5937, 78.9629

        env_data = geospatial_service.get_environmental_data(lat, lon)
        sensitivities = bio_data.get("sensitivities", {})
        risk = risk_estimator.estimate_risk(env_data, sensitivities)
        
        # Get Prescriptions
        actions = prescription_engine.recommend_actions(risk, "report_context", species_name, species_data=bio_data)
        
        # [FEATURE] Future Risk Prediction
        # Calculate Future Outlook based on 5-Year Trend + Climate
        climate_fc = bio_data.get("analysis", {}).get("climate", {})
        pop_hist = bio_data.get("population_history", [])
        
        future_outlook = risk_estimator.predict_future_risk(pop_hist, climate_fc)
        
        # [Updated Logic] Get granular stats for Report
        veg_data = trend_analyzer.simulate_daily_vegetation(env_data, days=5)
        dist_data = trend_analyzer.simulate_yearly_disturbance(env_data, years=5)
        climate_data = climate_predictor.predict_future_scenario(env_data)
        
        env_context = {
            "avg_ndvi": env_data.ndvi,
            "avg_temp": env_data.temperature_celsius,
            "avg_rain": env_data.rainfall_forecast_mm,
            "hdi": env_data.human_development_index,
            "risk_score": risk.risk_score,
            "future_outlook": future_outlook,
            # Add granular trends for the LLM
            "veg_trend": str(dict(zip(veg_data["labels"], veg_data["ndvi"]))),
            "climate_trend": str(dict(zip(climate_data["years"], climate_data["temp"]))),
            "dist_trend": str(dict(zip(dist_data["labels"], dist_data["nightlights"])))
        }

        # 2. Generate LLM Report
        report_text = report_service.generate_llm_report(
            species_name=species_name,
            species_data=bio_data,
            env_context=env_context,
            conservation_plan=[a.dict() for a in actions]
        )
        
        return {"report": report_text}
    except Exception as e:
        print(f"Report Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/report/download/{species_name}")
async def download_report_pdf(species_name: str, payload: dict):
    """
    Generates and returns a PDF file from the provided report text.
    """
    report_text = payload.get("report_text", "")
    pdf_path = report_service.generate_pdf_report(species_name, report_text)
    if not pdf_path or not os.path.exists(pdf_path):
        raise HTTPException(status_code=500, detail="Failed to generate PDF")
    
    return FileResponse(
        path=pdf_path,
        filename=os.path.basename(pdf_path),
        media_type="application/pdf"
    )
