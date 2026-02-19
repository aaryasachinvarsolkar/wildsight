
import sys
import os
from unittest.mock import MagicMock

# Mock Dependencies
sys.modules["google"] = MagicMock()
sys.modules["google.genai"] = MagicMock()
sys.modules["app.services.report"] = MagicMock()
sys.modules["app.models.db"] = MagicMock()
sys.modules["app.models.db"].engine = MagicMock()

# Add project root to path
# Script is in backend/scripts. 'app' is in backend.
# So we need to add 'backend' to sys.path, or add 'root' and import 'backend.app'.
# Based on biometric.py, it expects 'app' to be top level? 
# In backend/app/services/biometric.py: `from app.models.db...`
# So `backend` folder must be in sys.path.
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.services.biometric import biometric_service

def check():
    species = ["Indian Elephant", "Nilgiri Tahr"]
    
    with open("results_live.txt", "w", encoding="utf-8") as f:
        f.write("--- Live Counts ---\n")
        for s in species:
            try:
                print(f"Fetching {s}...")
                data = biometric_service.get_species_data(s)
                
                name = data.get("species_name")
                pop = data.get("estimated_population")
                
                # Try to extract context via debug or just infer
                sci = data.get("distribution_analysis", {}).get("scientific_context", {})
                
                f.write(f"\nSpecies: {s}\nResolved: {name}\nFinal Count: {pop}\n")
                f.write(f"Scientific Context: {sci}\n")
                
            except Exception as e:
                f.write(f"Error {s}: {e}\n")
                print(f"Error {s}: {e}")

if __name__ == "__main__":
    check()
