
import sys
import os
import asyncio
from unittest.mock import MagicMock

# Mock dependencies to run API logic in isolation
sys.modules["google"] = MagicMock()
sys.modules["google.genai"] = MagicMock()
# sys.modules["app.services.report"] = MagicMock() # Needed?
# sys.modules["app.models.db"] = MagicMock()

# Add project root
# Add project root
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# We need to test the result of the ROUTER function, 
# But that requires mocking the Request and DB.
# Instead, let's call biometric_service.get_species_data directly, 
# AND THEN apply the logic found in api/species.py

from app.services.biometric import biometric_service
from app.services.geospatial import geospatial_service
from app.services.intelligence import trend_analyzer, climate_predictor

def check_structure():
    print("Checking 'Tiger' data structure...")
    try:
        data = biometric_service.get_species_data("Tiger")
        
        # Simulate API logic in species.py
        if "analysis" in data:
            print("SUCCESS: 'analysis' key found in biometric response.")
            print(f"Keys: {data['analysis'].keys()}")
            print(f"Veg Labels: {data.get('days_vegetation')}")
        else:
            print("FAILURE: 'analysis' key MISSING in biometric response.")
            
        # Check estimated_population
        val = data.get("estimated_population")
        print(f"Estimated Population: {val}")

        # Check serialization safety
        import json
        try:
             # Basic serialization check
             json.dumps(data)
             print("SUCCESS: Data is JSON serializable.")
        except Exception as e:
             print(f"FAILURE: Data is NOT JSON serializable: {e}")
             # Debug fields
             for k, v in data.items():
                 try:
                     json.dumps({k:v})
                 except:
                     print(f"  Field '{k}' caused error.")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_structure()
