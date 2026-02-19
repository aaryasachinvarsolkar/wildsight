import sys
import os
import requests

# Add backend to path
sys.path.append(os.path.join(os.getcwd(), 'backend'))

from app.services.biometric import biometric_service

def test_gbif_direct():
    name = "Tiger"
    print(f"--- Testing GBIF Resolution for '{name}' ---")
    
    # 1. Resolve Name
    key, corrected_name, meta = biometric_service._resolve_name_smart(name)
    print(f"FINAL_KEY: {key}")
    print(f"FINAL_NAME: {corrected_name}")
    print(f"FINAL_META: {meta}")

    if not key:
        print("FAIL: No key returned.")
        return

    # 2. Fetch Data (Simulated)
    url = "https://api.gbif.org/v1/occurrence/search"
    params = {
        "taxonKey": key,
        "hasCoordinate": "true",
        "limit": 300, # Testing production limit
        "country": "IN",
        # "basisOfRecord": "HUMAN_OBSERVATION" 
    }
    
    print(f"\nFetching from: {url}")
    print(f"Params: {params}")
    
    try:
        res = requests.get(url, params=params, timeout=10)
        print(f"Status: {res.status_code}")
        data = res.json()
        count = data.get("count", 0)
        results = data.get("results", [])
        
        print(f"Total Count: {count}")
        print(f"Returned Results: {len(results)}")
        
        if len(results) > 0:
            print(f"Sample Result 1: {results[0].get('decimalLatitude')}, {results[0].get('decimalLongitude')}")
        else:
            print("NO RESULTS FOUND despite count > 0 (or count is 0)")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_gbif_direct()
