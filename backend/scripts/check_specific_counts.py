
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
# We need the folder containing 'app' (which is 'backend') to be in sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.services.biometric import biometric_service

def check_counts():
    species_list = ["Indian Elephant", "Nilgiri Tahr"]
    
    with open("results_counts.txt", "w", encoding="utf-8") as f:
        f.write("--- Checking Counts ---\n")
        for s in species_list:
            try:
                print(f"Querying: {s}...")
                data = biometric_service.get_species_data(s)
                
                name = data.get("species_name")
                pop = data.get("estimated_population")
                src = data.get("scientific_context", {}).get("scientific_source")
                trend = data.get("population_history", [])
                
                res = f"\nSpecies: {s}\nResolved: {name}\nCount: {pop}\nSource: {src}\n"
                if trend:
                    res += f"Trend2022: {trend[0]['count']}\nTrend2026: {trend[-1]['count']}\n"
                f.write(res)
                print(f"Done {s}")
            except Exception as e:
                f.write(f"\nError {s}: {e}\n")
                print(f"Error {s}")

if __name__ == "__main__":
    check_counts()
