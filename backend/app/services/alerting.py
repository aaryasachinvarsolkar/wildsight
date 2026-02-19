import math
from datetime import datetime
from app.models.db import PulseLog, RiskPrediction
from app.services.geospatial import geospatial_service
from app.services.ingest_gbif import gbif_service
from app.services.notifier import notifier_service

def calculate_distance(lat1, lon1, lat2, lon2):
    # Haversine formula
    R = 6371  # Earth radius in km
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat / 2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c

def analyze_and_alert_user(user, session):
    """
    Analyzes a single user's location for high-risk species and sends alerts.
    Designed to be called by scheduler OR immediately after registration.
    """
    if not user.latitude or not user.longitude:
        return []

    print(f"  Analysing radius for {user.full_name} ({user.email})...")
    
    # 2. Find species near this user (50km radius)
    local_species = gbif_service.fetch_species_near_location(user.latitude, user.longitude, radius_km=50)
    
    if not local_species:
        print(f"    No live species found near {user.latitude}, {user.longitude}. Using Demo Fallback.")
        local_species = [{"name": "Panthera tigris", "lat": user.latitude + 0.1, "lon": user.longitude + 0.1}]
    
    new_knowledge_logs = []
    
    for spec in local_species:
        species_name = spec['name']
        lat, lon = spec['lat'], spec['lon']
        dist = calculate_distance(user.latitude, user.longitude, lat, lon)
        
        # 3. Get Environmental Data and Run Intelligence
        env_data = geospatial_service.get_environmental_data(lat, lon)
        monitoring_ndvi = env_data.ndvi
        
        # AI Risk logic (simplified for pulse)
        # Dynamic risk based on NDVI: lower NDVI = higher risk
        risk_score = 0.3
        if monitoring_ndvi < 0.45: # Habitat stress
            risk_score = 0.82
        
        # 4. NOTIFY USER (Actual Alert)
        if risk_score > 0.7:
            print(f"    [ALERT] RED LEVEL: {species_name} is in danger at {dist:.1f}km from {user.full_name}")
            notifier_service.notify_user_about_species(
                user_email=user.email,
                user_name=user.full_name,
                species_name=species_name,
                distance_km=dist,
                risk_score=risk_score
            )
        
        # 5. Log for ML (Knowledge growth)
        trainer_log = {
            "species_name": species_name,
            "risk_score": risk_score,
            "ndvi_current": monitoring_ndvi,
            "action": "field_intervention" if risk_score > 0.7 else "monitor",
            "outcome": "success", 
            "hdi": 0.5, "sens_fire": 0, "sens_poaching": 0, "sens_encroachment": 0, "sens_drought": 0,
            "sens_disease": 0, "sens_power_lines": 0, "is_plant": 0, "is_mammal": 1,
            "is_bird": 0, "is_reptile": 0, "is_amphibian": 0, "is_insect": 0, "is_marine": 0, "is_fungi": 0
        }
        new_knowledge_logs.append(trainer_log)
        
        # 6. Save Log for History
        db_log = PulseLog(
            species_name=species_name,
            h3_index="radius_search",
            timestamp=datetime.utcnow(),
            population_count=100, # Placeholder
            risk_score=risk_score,
            data_source="radius_pipeline"
        )
        session.add(db_log)
        
    return new_knowledge_logs
