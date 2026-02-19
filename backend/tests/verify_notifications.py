import sys
import os
import requests
import time
from sqlmodel import Session, select

# Add backend to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.models.db import engine, User, PulseLog, create_db_and_tables
from app.services.notifier import notifier_service

def verify():
    print("--- Starting Verification ---")
    
    # 1. Ensure DB is clean and has tables
    create_db_and_tables()
    
    # 2. Mock User Registration
    with Session(engine) as session:
        # Check if test user exists
        statement = select(User).where(User.email == "test@example.com")
        user = session.exec(statement).first()
        if not user:
            print("Creating test user...")
            user = User(
                email="test@example.com",
                hashed_password="hashed_password",
                full_name="Test User",
                area_of_interest="India"
            )
            session.add(user)
            session.commit()
            session.refresh(user)
        else:
            print("Test user already exists.")

    # 3. Trigger a pulse-like event with high risk
    print("\nSimulating high-risk event for Tiger in India...")
    species = "Panthera tigris"
    area = "India"
    risk = 0.85
    
    # This simulates what happens in scheduler.py
    with Session(engine) as session:
        user_statement = select(User).where(User.area_of_interest == area)
        users = session.exec(user_statement).all()
        
        print(f"Found {len(users)} users to notify.")
        for u in users:
            print(f"Sending alert to {u.email}...")
            notifier_service.notify_user_about_species(
                user_email=u.email,
                user_name=u.full_name,
                species_name=species,
                area_name=area,
                risk_score=risk
            )
    
    print("\n--- Verification Complete ---")

if __name__ == "__main__":
    verify()
