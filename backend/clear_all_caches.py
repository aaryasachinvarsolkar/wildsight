from sqlmodel import Session, delete, select
from app.models.db import engine, RiskPrediction, EnvironmentalCache, EnvironmentalHistory

def clear_all_caches():
    print("Purging all database caches...")
    with Session(engine) as session:
        # Clear Risk Predictions
        session.exec(delete(RiskPrediction))
        # Clear Geospatial Caches
        session.exec(delete(EnvironmentalCache))
        # Clear Environmental History
        session.exec(delete(EnvironmentalHistory))
        session.commit()
    print("Purge complete. System will now recalculate everything at Level 6 resolution.")

if __name__ == "__main__":
    clear_all_caches()
