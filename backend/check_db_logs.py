from sqlmodel import Session, select
from app.models.db import engine, PulseLog
import datetime

def check_db():
    with Session(engine) as session:
        print("--- PulseLog Contents for Tiger ---")
        stmt = select(PulseLog).where(PulseLog.species_name == "Tiger").order_by(PulseLog.timestamp.desc())
        logs = session.exec(stmt).all()
        if not logs:
            print("No logs found for 'Tiger'.")
        for log in logs:
            print(f"ID: {log.id}, Time: {log.timestamp}, Count: {log.population_count}, Zone: {log.h3_index}")

        print("\n--- PulseLog Contents for Panthera tigris ---")
        stmt = select(PulseLog).where(PulseLog.species_name == "Panthera tigris").order_by(PulseLog.timestamp.desc())
        logs = session.exec(stmt).all()
        if not logs:
            print("No logs found for 'Panthera tigris'.")
        for log in logs:
            print(f"ID: {log.id}, Time: {log.timestamp}, Count: {log.population_count}, Zone: {log.h3_index}")

if __name__ == "__main__":
    check_db()
