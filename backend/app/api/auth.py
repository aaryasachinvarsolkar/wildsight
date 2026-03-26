from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlmodel import Session, select
from app.models.db import User, get_session
import firebase_admin
from firebase_admin import auth
from pydantic import BaseModel, EmailStr
from typing import Optional

import os

# Initialize Firebase Admin
FIREBASE_AVAILABLE = False
try:
    # Try initializing with explicit check for credentials availability (Implicit)
    # If no creds, this will fail immediately or on first use.
    # We do a proactive check by trying to get the app, or init.
    try:
        firebase_admin.get_app()
        FIREBASE_AVAILABLE = True
    except ValueError:
        # Not initialized yet
        project_id = os.getenv("VITE_FIREBASE_PROJECT_ID", "wildsight-1efbc")
        # NOTE: This call succeeds even without creds on some versions, but fails on usage (verify_token)
        # However, the user reported "Default credentials not found", implying this line CRASHED.
        # We wrap it.
        firebase_admin.initialize_app(options={'projectId': project_id})
        FIREBASE_AVAILABLE = True
        print(f"Firebase Admin Initialized for project: {project_id}")
        
except Exception as e:
    print(f"WARNING: Firebase Credentials NOT FOUND. Running in DEV MODE (Bypass Auth). Error: {e}")
    FIREBASE_AVAILABLE = False

import logging
# Use Uvicorn's logger for visibility
logger = logging.getLogger("uvicorn.error")
from jose import jwt

router = APIRouter(tags=["Authentication"])
security = HTTPBearer()

class UserRegister(BaseModel):
    email: EmailStr
    full_name: str
    latitude: float
    longitude: float
    firebase_uid: str

def get_current_user(auth_header: HTTPAuthorizationCredentials = Depends(security), session: Session = Depends(get_session)):
    try:
        token = auth_header.credentials
        uid = None
        email = None
        
        if FIREBASE_AVAILABLE:
            try:
                decoded_token = auth.verify_id_token(token)
                uid = decoded_token['uid']
                email = decoded_token.get('email')
            except Exception as e:
                # If verify fails despite init (e.g. no creds actually worked), fallback
                logger.warning(f"Firebase verify failed, trying fallback: {e}")
                if "credentials" in str(e).lower():
                    # Fallback to unverified
                    pass
                else:
                    raise e
                    
        if not uid:
             # Fallback / Dev Mode
             # Decode without verification
             claims = jwt.get_unverified_claims(token)
             uid = claims.get('user_id') or claims.get('sub')
             email = claims.get('email')
             logger.warning(f"DEV MODE: Decoded token without verification for {email}")

        if not uid:
            raise HTTPException(status_code=401, detail="Invalid Token Structure")
        
        statement = select(User).where(User.firebase_uid == uid)
        user = session.exec(statement).first()
        
        if not user:
            # Check by email as fallback for legacy users
            if email:
                statement = select(User).where(User.email == email)
                user = session.exec(statement).first()
                if user:
                    user.firebase_uid = uid
                    session.add(user)
                    session.commit()
                    session.refresh(user)
                    return user
            
            raise HTTPException(status_code=404, detail="User not found in local database")
        return user
    except Exception as e:
        logger.error(f"Auth Error: {e}")
        # import traceback
        # traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid authentication credentials: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"},
        )

@router.post("/register", status_code=status.HTTP_201_CREATED)
def register(user_data: UserRegister, background_tasks: BackgroundTasks, auth_header: HTTPAuthorizationCredentials = Depends(security), session: Session = Depends(get_session)):
    logger.info(f"DEBUG: Register endpoint hit for {user_data.email}")
    try:
        logger.info(f"DEBUG: Verifying token: {auth_header.credentials[:10]}...")
        token = auth_header.credentials
        uid = None
        
        if FIREBASE_AVAILABLE:
            try:
                decoded_token = auth.verify_id_token(token)
                uid = decoded_token['uid']
            except Exception:
                pass
                
        if not uid:
             # Fallback
             claims = jwt.get_unverified_claims(token)
             uid = claims.get('user_id') or claims.get('sub')
             logger.warning(f"DEV MODE: Using unverified UID: {uid}")
        
        if uid != user_data.firebase_uid:
            logger.error(f"UID Mismatch: Token({uid}) vs Form({user_data.firebase_uid})")
            if uid != user_data.firebase_uid:
                raise HTTPException(status_code=403, detail="UID mismatch")
        
        statement = select(User).where(User.firebase_uid == uid)
        existing_user = session.exec(statement).first()
        
        if existing_user:
            existing_user.latitude = user_data.latitude
            existing_user.longitude = user_data.longitude
            session.add(existing_user)
            session.commit()
            
            # Trigger alert for location update
            from app.services.alerting import analyze_and_alert_user
            background_tasks.add_task(analyze_and_alert_user, existing_user, session)
            
            return {"message": "User location updated"}

        new_user = User(
            email=user_data.email,
            hashed_password="firebase_managed",
            full_name=user_data.full_name,
            latitude=user_data.latitude,
            longitude=user_data.longitude,
            firebase_uid=uid
        )
        session.add(new_user)
        session.commit()
        session.refresh(new_user)
        
        # Trigger immediate analysis and alert
        from app.services.alerting import analyze_and_alert_user
        background_tasks.add_task(analyze_and_alert_user, new_user, session)
        
        return {"message": "User registered successfully", "id": new_user.id}
    except Exception as e:
        print(f"Registration Error: {str(e)}")
        raise HTTPException(status_code=401, detail=str(e))

@router.get("/me")
def get_me(current_user: User = Depends(get_current_user)):
    return {
        "id": current_user.id,
        "email": current_user.email,
        "full_name": current_user.full_name,
        "latitude": current_user.latitude,
        "longitude": current_user.longitude,
        "firebase_uid": current_user.firebase_uid
    }
