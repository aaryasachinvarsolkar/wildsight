import sys
import os
import traceback

# Add backend to path
sys.path.append(os.path.join(os.getcwd(), 'backend'))

from app.services.biometric import biometric_service

def test_direct():
    print("--- Testing BiometricService Direct Call for 'Tiger' ---")
    try:
        data = biometric_service.get_species_data("Tiger", zone_id="8928308280fffff")
        
        checkpoints = data.get("checkpoints", [])
        print(f"CHECKPOINTS_COUNT: {len(checkpoints)}")
        
        dist = data.get("distribution_analysis", {})
        zones = dist.get("zones", [])
        print(f"ZONES_COUNT: {len(zones)}")
        
        if len(zones) > 0:
            print(f"FIRST_ZONE: {zones[0]['name']} (Count: {zones[0]['sighting_count']})")
        
    except Exception:
        traceback.print_exc()

if __name__ == "__main__":
    test_direct()
