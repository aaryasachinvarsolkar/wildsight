import sys
import os
from dotenv import load_dotenv

load_dotenv(os.path.join(os.getcwd(), 'backend', '.env'))

# Add backend to path
sys.path.append(os.path.join(os.getcwd(), 'backend'))

from app.services.biometric import biometric_service
from app.services.report import report_service

def trace():
    print("--- SURGICAL TRACE: TIGER CENSUS ---")
    species = "Panthera tigris"
    res = biometric_service._fetch_census_from_llm(species)
    print(f"AI CENSUS RESULT: {res}")

if __name__ == "__main__":
    trace()
