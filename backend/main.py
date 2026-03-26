from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os

load_dotenv()

from app.api import router as api_router
import logging

# Use Uvicorn's logger
logger = logging.getLogger("uvicorn.error")

app = FastAPI(
    title="EcoGuard Geospatial Intelligence Platform",
    description="Advanced AI-powered Geospatial Intelligence Platform for Biodiversity Conservation",
    version="1.0.0"
)

# CORS Configuration
origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

from fastapi import Request
import traceback
import sys

@app.on_event("startup")
async def startup_event():
    logger.info("STARTUP: EcoGuard Backend Initialized with Logging")

@app.middleware("http")
async def log_exceptions_middleware(request: Request, call_next):
    logger.info(f"DEBUG MIDDLEWARE: Request: {request.method} {request.url}")
    logger.info(f"DEBUG MIDDLEWARE: Headers: {request.headers}")
    try:
        return await call_next(request)
    except Exception as e:
        logger.error(f"CRITICAL API ERROR: {e}")
        traceback.print_exc()
        from fastapi.responses import JSONResponse
        return JSONResponse(
            status_code=500,
            content={"detail": str(e), "traceback": traceback.format_exc()}
        )

@app.get("/")
def read_root():
    return {"message": "Welcome to EcoGuard API"}

app.include_router(api_router, prefix="/api/v1")
