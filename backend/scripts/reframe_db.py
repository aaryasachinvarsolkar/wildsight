from app.models.db import engine, EnvironmentalHistory, EnvironmentalCache, PulseLog
from app.services.biometric import BiometricService
from app.services.geospatial import GeospatialService
from sqlmodel import Session, delete, select
import time

def reframe_database():
    print("--- REFRAMING WILD SIGHT DATABASE WITH REAL DATA ---")
    bio = BiometricService()
    geo = GeospatialService()
    
    # 1. Clear Simulated/Old Historical Logs to make room for Real Grounded History
    with Session(engine) as session:
        print("Clearing old simulated logs...")
        session.exec(delete(EnvironmentalHistory))
        session.exec(delete(EnvironmentalCache))
        session.exec(delete(PulseLog))
        session.commit()

    # 2. Prefetch Real Data for Target Species
    targets = ["Tiger", "Asian Elephant", "Indian Rhino", "Great Indian Bustard"]
    
    for species in targets:
        print(f"\nProcessing {species}...")
        try:
            # This triggers:
            # a) Realistic GBIF sighting fetch (limit 300)
            # b) Real year facet fetch (2021-2025)
            # c) Scientific error calibration (18x-40x multipliers)
            # d) Parallel Sentinel Hub historical telemetry (5 years of real pixels)
            data = bio.get_species_data(species)
            
            pop = data['estimated_population']
            status = data['status']
            print(f"SUCCESS: {species} grounded.")
            print(f" -> Real-World Est: {pop}")
            print(f" -> IUCN Status: {status}")
            print(f" -> History Points: {len(data['population_history'])}")
            
        except Exception as e:
            print(f"FAILED {species}: {e}")
        
        time.sleep(1)

    print("\n--- DATABASE REFRAMED SUCCESSFULLY ---")

if __name__ == "__main__":
    reframe_database()
