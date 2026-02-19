import sys
import os
import math

# Add backend to path
sys.path.append(os.path.join(os.getcwd(), 'backend'))

from app.services.biometric import biometric_service

def find_nan(obj, path=""):
    if isinstance(obj, dict):
        for k, v in obj.items():
            find_nan(v, path + f".{k}")
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            find_nan(v, path + f"[{i}]")
    elif isinstance(obj, float):
        if math.isnan(obj) or math.isinf(obj):
            print(f"FOUND NaN/Inf at: {path} = {obj}")

def test_nan():
    print("--- Searching for NaN values ---")
    try:
        # Fetch the data that causes the crash
        data = biometric_service.get_species_data("Tiger", zone_id="8928308280fffff")
        find_nan(data, "root")
        print("Scan complete.")
    except Exception as e:
        print(f"Error during fetch: {e}")

if __name__ == "__main__":
    test_nan()
