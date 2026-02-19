import sys
import os
# Add the 'backend' folder to sys.path
# File is in backend/tests/manual/update_db.py
# 1: manual, 2: tests, 3: backend
backend_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(backend_dir)
from app.models.db import create_db_and_tables
create_db_and_tables()
print("Success: Database schema updated with PlaceNameCache.")
