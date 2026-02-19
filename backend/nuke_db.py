from sqlmodel import Session, select, delete, text
from app.models.db import engine, PulseLog, EnvironmentalHistory, PlaceNameCache, EnvironmentalCache

def clear_all():
    print("--- NUKE PROTOCOL INITIATED ---")
    with Session(engine) as session:
        print("Deleting PulseLog...")
        session.exec(delete(PulseLog))
        
        print("Deleting EnvironmentalHistory...")
        session.exec(delete(EnvironmentalHistory))
        
        # Optional: Clear Cache if needed, but not critical for population
        # session.exec(delete(EnvironmentalCache))
        
        session.commit()
    print("--- DATABASE CLEARED ---")

if __name__ == "__main__":
    clear_all()
