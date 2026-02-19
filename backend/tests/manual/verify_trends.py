import requests
import json

def verify():
    print("Verifying Location-Aware Trends (WildSight v1.4)...")
    url = "http://localhost:8000/api/v1/species/Tiger"
    
    # 1. Fetch Zone A
    res1 = requests.get(url)
    data1 = res1.json().get("species", {})
    pulse1 = data1.get("pulse_history", [])
    ndvi1 = data1.get("analysis", {}).get("vegetation", {}).get("ndvi", [])
    
    # We need to find a way to switch zones in the test. 
    # Usually clicking a zone in the UI calls with ?zone_id=...
    # Let's try to find an H3 index from the first response.
    zones = data1.get("distribution_analysis", {}).get("zones", [])
    if not zones:
        print("Error: No zones found to test.")
        return

    h3_a = zones[0]['id']
    h3_b = zones[1]['id'] if len(zones) > 1 else "8460595ffffffff"

    print(f"Testing Zone A: {h3_a}")
    res_a1 = requests.get(f"{url}?zone_id={h3_a}")
    trend_a1 = res_a1.json()['species']['analysis']['vegetation']['ndvi']
    
    res_a2 = requests.get(f"{url}?zone_id={h3_a}")
    trend_a2 = res_a2.json()['species']['analysis']['vegetation']['ndvi']
    
    if trend_a1 == trend_a2:
        print("✅ CONSISTENCY: Zone A returned identical trends twice.")
    else:
        print("❌ FAILURE: Zone A returned different trends.")

    print(f"Testing Zone B: {h3_b}")
    res_b = requests.get(f"{url}?zone_id={h3_b}")
    trend_b = res_b.json()['species']['analysis']['vegetation']['ndvi']
    
    if trend_a1 != trend_b:
        print("✅ UNIQUENESS: Zone A and Zone B have distinct trends.")
    else:
        print("❌ FAILURE: Zone A and Zone B trends are identical.")

if __name__ == "__main__":
    verify()
