from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Literal
from datetime import datetime

class BiometricFeature(BaseModel):
    species_name: str
    observation_date: datetime
    latitude: float
    longitude: float
    confidence: float
    source: str = Field(..., description="GBIF, iNaturalist, etc.")
    is_cached: bool = False

class EnvironmentalData(BaseModel):
    ndvi: float
    evi: float = 0.5 # Enhanced Vegetation Index
    ndwi: float
    rainfall_forecast_mm: float
    temperature_celsius: float
    fire_radiative_power: float
    human_development_index: float
    nightlights: float = 0.0 # Proxy for urban pressure
    h3_index: Optional[str] = None # Added for location-aware trending
    place_name: Optional[str] = "Unknown Habitat"
    is_cached: bool = False

class RiskAssessment(BaseModel):
    risk_score: float = Field(..., ge=0.0, le=1.0)
    primary_stressor: str  # Changed from Literal to allow dynamic stressors
    anomaly_detected: bool
    details: Optional[Dict[str, float]] = {}

class Prescription(BaseModel):
    action_type: str # Changed from Literal to allow dynamic actions from ML
    priority: str = "medium"
    description: str
    target_zone_h3: str
    estimated_cost: float
    expected_outcome: str

class ZoneAnalysis(BaseModel):
    h3_index: str
    environment: EnvironmentalData
    risk: RiskAssessment
    prescriptions: List[Prescription]
