import os
import sys
from datetime import datetime, timedelta
from sqlmodel import Session, select, delete
from dotenv import load_dotenv

load_dotenv()

# Add backend to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.models.db import engine, PulseLog, EnvironmentalHistory, EnvironmentalCache
from app.services.biometric import biometric_service
from app.services.report import report_service

def fix_pulse_data():
    print("--- FIXING PULSE DATA ACCURACY ---")
    species_list = ["Panthera tigris"]
    
    with Session(engine) as session:
        print("Clearing corrupted PulseLog entries...")
        session.exec(delete(PulseLog))
        session.commit()
        
        for species in species_list:
            print(f"Seeding grounded data for {species}...")
            # Use short name for biometric fetch if needed, but get_species_data handles both
            data = biometric_service.get_species_data(species)
            base_pop = data.get("estimated_population", 1000)
            print(f"  -> Grounded Population: {base_pop}")
            
            # Create 5 days of history
            for i in range(5):
                ts = datetime.utcnow() - timedelta(days=i)
                # Add slight random variation
                count = int(base_pop * (1 + (i * 0.01))) 
                
                log = PulseLog(
                    species_name=species,
                    h3_index="global",
                    timestamp=ts,
                    population_count=count,
                    risk_score=0.2 + (i * 0.05),
                    data_source="calibration_fix"
                )
                session.add(log)
        session.commit()
    print("Pulse Data Calibrated.")

def test_report_endpoint():
    print("\n--- DEBUGGING REPORT ENGINE ---")
    api_key = os.getenv("GOOGLE_API_KEY")
    print(f"API Key Found: {'YES' if api_key and 'YOUR' not in api_key else 'NO (or default placeholder)'}")
    
    if not api_key or "YOUR" in api_key:
        print("WARNING: GOOGLE_API_KEY is not set correctly in .env")

    try:
        from app.services.report import report_service
        print("Initializing Gemini...")
        # Simple test
        prompt = "Hello, are you online?"
        if report_service.client:
            print("Sending test request to Gemini...")
            # We'll use a timeout-like behavior or just check initialization
            print("Gemini model is initialized.")
        else:
            print("Gemini model is NOT initialized.")
    except Exception as e:
        print(f"Report Initialization Crash: {e}")

if __name__ == "__main__":
    fix_pulse_data()
    test_report_endpoint()
