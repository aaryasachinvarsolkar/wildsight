from fastapi import APIRouter
from app.api import species

router = APIRouter()

@router.get("/health")
def health_check():
    return {"status": "healthy"}

router.include_router(species.router, prefix="/species", tags=["species"])
from app.api import v1_analytics
router.include_router(v1_analytics.router, prefix="/analytics", tags=["analytics"])
from app.api import auth
router.include_router(auth.router, prefix="/auth", tags=["auth"])
