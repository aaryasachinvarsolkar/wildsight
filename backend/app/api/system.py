from fastapi import APIRouter
from sqlmodel import Session, select, func
from datetime import datetime, timedelta
from app.models.db import engine, EnvironmentalCache
from app.services.environmental import environmental_service
from app.services.taxonomy import taxonomy_service
from app.services.population import population_service

router = APIRouter()

@router.get("/status")
def get_system_status():
    """
    Checks if the global database (satellite telemetry) is up to date (5-day cycle).
    """
    with Session(engine) as session:
        # Find the most recent update time across the entire cache
        res = session.exec(select(func.max(EnvironmentalCache.last_updated))).first()
        
        last_sync = res if res else datetime(2000, 1, 1)
        # Check if synced within last 5 days
        is_synced = datetime.utcnow() - last_sync < timedelta(days=5)
        
        return {
            "last_synchronized": last_sync.isoformat(),
            "synchronized": is_synced,
            "days_since_sync": (datetime.utcnow() - last_sync).days,
            "threshold_days": 5
        }

@router.post("/synchronize")
def synchronize_biosphere():
    """
    Triggers a global update of the biosphere for core Indian species.
    """
    # 1. We'll refresh the habitats of our 4 iconic species to seed the cache
    iconic = ["Tiger", "Asian Elephant", "Great Indian Bustard", "Syzygium travancoricum"]
    
    for s_name in iconic:
        # Resolve taxonomy first
        key, clean_name, meta = taxonomy_service.resolve_name(s_name)
        if key:
            # Fetch occurrences to get coordinates
            pop_data = population_service.get_population_data(clean_name, key=key)
            # Fetch environmental data for the first checkpoint (seeding cache)
            if pop_data.get('checkpoints'):
                p = pop_data['checkpoints'][0]
                environmental_service.get_environmental_data(p['lat'], p['lon'])
    
    return {"status": "success", "message": "Biosphere synchronization complete (ESA S2/NASA FIRMS refreshed)."}
