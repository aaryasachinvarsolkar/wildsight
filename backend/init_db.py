import sys
import os
from sqlmodel import SQLModel

# Add backend to path to allow imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.models.db import engine, create_db_and_tables, RiskPrediction, EnvironmentalCache, PulseLog

def init():
    print("Initializing Database...")
    if os.path.exists("wildsight.db"):
        print("Removing old database for clean state (Dev Mode)...")
        try:
            os.remove("wildsight.db")
        except PermissionError:
            print("Warning: Could not delete wildsight.db (might be in use). Operations might fail if schema changed.")
    
    create_db_and_tables()
    print("Database `wildsight.db` created with tables:")
    print("- RiskPrediction")
    print("- EnvironmentalCache")
    print("- PulseLog")
    print("Done.")

if __name__ == "__main__":
    init()
