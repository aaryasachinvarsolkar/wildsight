from sqlmodel import Session, delete
from app.models.db import engine, RiskPrediction

def clear_risk_cache():
    print("Purging stale AI error messages from RiskPrediction cache...")
    with Session(engine) as session:
        session.exec(delete(RiskPrediction))
        session.commit()
    print("Risk Cache Cleared. Backend will now use updated fallback templates.")

if __name__ == "__main__":
    clear_risk_cache()
