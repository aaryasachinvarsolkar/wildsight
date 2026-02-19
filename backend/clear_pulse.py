from sqlmodel import Session, delete
from app.models.db import engine, PulseLog

def clear_logs():
    print("Clearing PulseLog table...")
    with Session(engine) as session:
        session.exec(delete(PulseLog))
        session.commit()
    print("PulseLog Cleared.")

if __name__ == "__main__":
    clear_logs()
