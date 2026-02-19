import sys
import os
from pathlib import Path

# Add current directory to path
sys.path.append(os.getcwd())
# Add backend to path
sys.path.append(os.path.join(os.getcwd(), "backend"))

from backend.app.services.biometric import biometric_service
from backend.app.models.db import engine, PulseLog
from sqlmodel import Session, select

def diagnose():
    species_to_test = ["Tiger", "Elephant"]
    for s in species_to_test:
        print(f"--- Diagnosing '{s}' ---")
        data = biometric_service.get_species_data(s)
        resolved_name = data.get("species_name")
        print(f"Resolved Name: '{resolved_name}'")
        
        with Session(engine) as session:
            # Check exact matches
            logs = session.exec(select(PulseLog).where(PulseLog.species_name == resolved_name)).all()
            print(f"Exact DB Matches for '{resolved_name}': {len(logs)}")
            
            if not logs:
                # Check all names in DB to see what we have
                all_names = session.exec(select(PulseLog.species_name).distinct()).all()
                print(f"Names actually in DB: {all_names}")

if __name__ == "__main__":
    diagnose()
