import sys
import os
from pathlib import Path

# Add backend to path
sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

from app.services.biometric import biometric_service

def test_robustness():
    # 1. Test Messy Name Cleaning
    messy_name = "Panthera tigris (Linnaeus, 1758)"
    print(f"\n--- Testing Robust Name Cleaning for: {messy_name} ---")
    data = biometric_service.get_species_data(messy_name)
    print(f"Resolved Name: {data.get('species_name')}")
    assert data.get('species_name') == "Panthera tigris"
    print("SUCCESS: Name cleaned and resolved.")

    # 2. Test Zone Lookup (Fixing the KeyError)
    print(f"\n--- Testing Zone Lookup (KeyError Fix) ---")
    # We need a real zone ID from the distribution analysis
    spatial = data.get("distribution_analysis", {})
    zones = spatial.get("zones", [])
    if zones:
        zone_id = zones[0]["id"]
        print(f"Testing for Zone: {zone_id}")
        # This used to raise KeyError
        data_zone = biometric_service.get_species_data("Tiger", zone_id=zone_id)
        print(f"Zone Data Pop: {data_zone.get('estimated_population')}")
        print("SUCCESS: Zone lookup completed without KeyError.")
    else:
        print("SKIP: No zones found to test.")

    # 3. Test Generic Name
    print(f"\n--- Testing Generic Name: 'Tiger' ---")
    data_tiger = biometric_service.get_species_data("Tiger")
    print(f"Resolved Name: {data_tiger.get('species_name')}")
    print(f"Pop History: {len(data_tiger.get('population_history', []))} yrs")

if __name__ == "__main__":
    try:
        test_robustness()
        print("\nALL LOCAL TESTS PASSED!")
    except Exception as e:
        print(f"\nTEST FAILED: {e}")
        import traceback
        traceback.print_exc()
