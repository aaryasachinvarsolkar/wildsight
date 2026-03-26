from typing import Optional, List, Dict
from sqlmodel import Field, SQLModel, create_engine, Session, JSON, select
from datetime import datetime
import os

# --- Database Setup ---
# Use absolute path for reliability in this environment
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DB_PATH = os.path.join(BASE_DIR, "wildsight.db")
DATABASE_URL = f"sqlite:///{DB_PATH}"

engine = create_engine(
    DATABASE_URL, 
    echo=False, 
    connect_args={"check_same_thread": False, "timeout": 30}
)

def enable_wal_mode():
    with engine.connect() as conn:
        conn.exec_driver_sql("PRAGMA journal_mode=WAL")

enable_wal_mode()

def get_session():
    with Session(engine) as session:
        yield session

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

# --- Models ---

class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    email: str = Field(index=True, unique=True)
    hashed_password: str
    full_name: str
    area_of_interest: str = Field(default="India") # Default area for notifications
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    firebase_uid: Optional[str] = Field(default=None, index=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)

class RiskPrediction(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    species_name: str = Field(index=True)
    h3_index: str = Field(index=True)
    
    # Risk Assessment
    risk_level: str  # Low, Medium, High
    confidence: float
    explanation: str
    
    # Context (Snapshot for debugging)
    features_snapshot: Dict = Field(default={}, sa_type=JSON) 
    
    # Metadata
    model_version: str = Field(default="1.0.0")
    prediction_source: str = Field(default="computed") # "cached" or "computed"
    created_at: datetime = Field(default_factory=datetime.utcnow) 

class EnvironmentalCache(SQLModel, table=True):
    """
    Cache for environmental data per H3 cell to avoid re-fetching constantly.
    """
    h3_index: str = Field(primary_key=True)
    ndvi: float
    evi: float = 0.5
    ndwi: float
    rainfall: float
    temperature: float
    human_development_index: float
    nightlights: float = 0.0
    fetched_at: datetime = Field(default_factory=datetime.utcnow) 
    last_updated: datetime = Field(default_factory=datetime.utcnow)

class PulseLog(SQLModel, table=True):
    """
    Log of 5-day updates for species population and risk.
    """
    id: Optional[int] = Field(default=None, primary_key=True)
    species_name: str = Field(index=True)
    h3_index: Optional[str] = Field(default=None, index=True) # [Phase 3] Added for location-specific graphs
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    population_count: int
    risk_score: float
    data_source: str = "computed"

class PlaceNameCache(SQLModel, table=True):
    """
    Persistent cache for Nominatim Reverse Geocoding results.
    """
    h3_index: str = Field(primary_key=True)
    full_name: str
    last_updated: datetime = Field(default_factory=datetime.utcnow)

class EnvironmentalHistory(SQLModel, table=True):
    """
    Historical time-series of environmental data per H3 cell.
    Populated by the continuous pulse pipeline.
    """
    id: Optional[int] = Field(default=None, primary_key=True)
    h3_index: str = Field(index=True)
    timestamp: datetime = Field(default_factory=datetime.utcnow, index=True)
    
    # Telemetry
    ndvi: float
    evi: float = 0.5
    ndwi: float
    temperature: float
    rainfall: float
    frp: float  # Fire Radiative Power
    hdi: float  # Human Development Index
    nightlights: float = 0.0
