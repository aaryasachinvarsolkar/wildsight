import requests
import json

def test_species_api(species="Tiger"):
    url = f"http://localhost:8000/api/v1/species/{species}"
    try:
        print(f"Testing API for {species}...")
        res = requests.get(url)
        res.raise_for_status()
        data = res.json()
        
        species_data = data.get("species", {})
        pop_hist = species_data.get("population_history", [])
        
        print(f"SUCCESS: API responded for {species}")
        print(f"Status: {species_data.get('status')}")
        print(f"Population History Count: {len(pop_hist)}")
        if pop_hist:
            print(f"Sample History: {pop_hist[0]}")
            
        analysis = species_data.get("analysis", {})
        ndvi_data = analysis.get("vegetation", {}).get("ndvi", [])
        print(f"NDVI History Count: {len(ndvi_data)}")
        
        # Verify no NaNs or Infs
        raw_json = json.dumps(data)
        if "NaN" in raw_json or "Infinity" in raw_json:
            print("ERROR: Response contains invalid JSON numbers (NaN/Infinity)")
        else:
            print("Response is clean of invalid numbers.")
            
    except Exception as e:
        print(f"FAILED: {e}")

if __name__ == "__main__":
    # Note: Backend must be running for this to work
    test_species_api("Tiger")
    test_species_api("Elephant")
