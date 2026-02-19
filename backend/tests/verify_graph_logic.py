import requests
import json
import os
import sys

# Add backend to path to import services directly if needed, 
# but testing via API is better for integration test.

API_URL = "http://localhost:8000/api/v1"

def test_species_intelligence():
    print("Testing /species/Tiger endpoint...")
    try:
        response = requests.get(f"{API_URL}/species/Tiger")
        if response.status_code != 200:
            print(f"FAILED: Status {response.status_code}")
            return False
            
        data = response.json()["species"]
        
        # Check for new fields
        if "days_vegetation" not in data:
            print("FAILED: 'days_vegetation' missing from response")
            return False
        if len(data["days_vegetation"]) != 5:
             print(f"FAILED: 'days_vegetation' length is {len(data['days_vegetation'])}, expected 5")
             return False
             
        if "years_disturbance" not in data:
            print("FAILED: 'years_disturbance' missing from response")
            return False
        if len(data["years_disturbance"]) != 5:
             print(f"FAILED: 'years_disturbance' length is {len(data['years_disturbance'])}, expected 5")
             return False
             
        # Check Analysis data alignment
        veg_ndvi = data["analysis"]["vegetation"]["ndvi"]
        if len(veg_ndvi) != 5:
            print(f"FAILED: Vegetation NDVI data length is {len(veg_ndvi)}, expected 5")
            return False
            
        dist_frp = data["analysis"]["disturbance"]["frp"]
        if len(dist_frp) != 5:
            print(f"FAILED: Disturbance FRP data length is {len(dist_frp)}, expected 5")
            return False

        print("SUCCESS: Species API returns correct granular data structure.")
        return True
    except Exception as e:
        print(f"ERROR: {e}")
        return False

def test_report_endpoint():
    print("\nTesting /analytics/report/Tiger endpoint (PDF Context)...")
    # This endpoint returns the LLM text. We can't easily check the *inputs* to the LLM 
    # without mocking, but we can check if it generates successfully.
    # Ideally, we should check logs or use a debug endpoint, but for now we ensure 500s don't occur
    # and the text (if mocked or generated) is returned.
    
    try:
        response = requests.get(f"{API_URL}/analytics/report/Tiger")
        if response.status_code != 200:
             print(f"FAILED: Report generation failed with {response.status_code}")
             print(response.text)
             return False
             
        report = response.json().get("report", "")
        if not report:
             print("FAILED: Report text is empty")
             return False
             
        print("SUCCESS: Report generation API works.")
        return True
    except Exception as e:
        print(f"ERROR: {e}")
        return False

if __name__ == "__main__":
    s1 = test_species_intelligence()
    s2 = test_report_endpoint()
    
    if s1 and s2:
        print("\nALL TESTS PASSED")
        sys.exit(0)
    else:
        print("\nSOME TESTS FAILED")
        sys.exit(1)
