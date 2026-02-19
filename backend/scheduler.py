import sys
import os
import time
from datetime import datetime
from sqlmodel import Session, select
import math

# Add backend to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.models.db import engine, RiskPrediction, PulseLog, User
from app.services.geospatial import geospatial_service
from app.services.ingest_gbif import gbif_service
from app.services.inference import inference_engine
from app.services.ml_trainer import MLTrainer
from app.services.notifier import notifier_service
from app.services.alerting import analyze_and_alert_user

def run_pulse():
    print(f"[{datetime.now()}] --- Pulse Started (Location-Aware Alerts) ---")
    trainer = MLTrainer()
    
    with Session(engine) as session:
        # 1. Get all registered users
        users = session.exec(select(User)).all()
        print(f"Monitoring habitats for {len(users)} users...")
        
        all_logs = []
        for user in users:
            logs = analyze_and_alert_user(user, session)
            if logs:
                all_logs.extend(logs)
                
        session.commit()
    
    # Retrain ML if new data points collected
    if all_logs:
        trainer.update_and_retrain(all_logs)

    print(f"[{datetime.now()}] --- Pulse Complete ---")

if __name__ == "__main__":
    run_pulse()
