from sqlmodel import Session
from app.models.db import engine, PulseLog
from datetime import datetime, timedelta
import random
import h3

def seed_history():
    print("Seeding Pulse History (Global + Local Zones)...")
    # Clean canonical names to match GBIF fix
    species_map = {
        "Panthera tigris": ["8460597ffffffff", "8460595ffffffff"], # Typical H3 clusters for tigers in India
        "Elephas maximus": ["8460517ffffffff", "8460515ffffffff"]
    }
    
    today = datetime(2026, 1, 5)
    
    with Session(engine) as session:
        # Clear old logs to avoid noise
        # session.exec("DELETE FROM pulselog") 
        
        for species_name, zones in species_map.items():
            base_pop = 3682 if "Panthera" in species_name else 27312
            
            # 1. Global Logs (no h3_index)
            for i in range(5):
                ts = today - timedelta(days=i)
                log = PulseLog(
                    species_name=species_name,
                    timestamp=ts,
                    population_count=base_pop - (i * random.randint(5, 15)),
                    risk_score=0.4 + (i * 0.02),
                    data_source="global_telemetry"
                )
                session.add(log)

            # 2. Zone Specific Logs (the "Graphs must change per location" requirement)
            for z_index in zones:
                zone_pop = int(base_pop / 10) # Smaller local population
                for i in range(5):
                    ts = today - timedelta(days=i)
                    # Different trend for local zone
                    log = PulseLog(
                        species_name=species_name,
                        h3_index=z_index,
                        timestamp=ts,
                        population_count=zone_pop + (i * random.randint(-5, 5)), # Local fluctuation
                        risk_score=0.3 + (i * 0.05),
                        data_source="zone_sensor_feed"
                    )
                    session.add(log)
                    print(f"Added Zone Log: {species_name} @ {z_index} | {ts.date()}")
                
        session.commit()
    print("Seeding Complete.")

if __name__ == "__main__":
    seed_history()
