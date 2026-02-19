import sys
import os
import requests
import json

def test_checkpoints():
    print("START_DEBUG")
    try:
        response = requests.get("http://localhost:8000/api/v1/species/Tiger")
        if response.status_code != 200:
            print(f"FAIL_STATUS: {response.status_code}")
            return

        data = response.json()
        species_data = data.get("species", {})
        
        checkpoints = species_data.get("checkpoints", [])
        print(f"CHECKPOINTS_COUNT: {len(checkpoints)}")
        
        dist = species_data.get("distribution_analysis", {})
        zones = dist.get("zones", [])
        print(f"ZONES_COUNT: {len(zones)}")
        
        if len(zones) > 0:
            print(f"FIRST_ZONE: {zones[0]['name']} (Count: {zones[0]['sighting_count']})")
        else:
            print("NO_ZONES_FOUND")

    except Exception as e:
        print(f"SCRIPT_ERROR: {e}")
    print("END_DEBUG")

if __name__ == "__main__":
    test_checkpoints()
