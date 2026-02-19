import requests
import json
import h3

def test_ecosystem_api():
    print("Testing Ecosystem Prediction API (Phase 3)...")
    
    # 1. Tiger in a specific location (Kanha National Park region approx)
    lat, lon = 22.33, 80.61
    try:
        h3_index = h3.geo_to_h3(lat, lon, 4)
    except AttributeError:
        h3_index = h3.latlng_to_cell(lat, lon, 4)
        
    print(f"Target H3 Index: {h3_index}")
    
    # 2. Call the API
    url = f"http://localhost:8000/api/v1/analytics/prescriptions/{h3_index}?species=Tiger"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            print("\nAPI Response Success!")
            
            risk_details = data.get("risk_assessment", {}).get("details", {})
            print(f"Predicted Count: {risk_details.get('predicted_count')}")
            print(f"Predicted Status: {risk_details.get('predicted_status')}")
            print(f"Habitat Quality: {risk_details.get('habitat_quality')}")
            print(f"Urban Pressure: {risk_details.get('urban_pressure')}")
            
            # Check Meta
            meta = data.get("meta", {})
            print(f"Model Version: {meta.get('model_version')}")
            
            # Check Actions
            actions = data.get("recommended_actions", [])
            for a in actions:
                print(f"\nAction: {a.get('action_type')}")
                print(f"Priority: {a.get('priority')}")
                # print(f"Description sample: {a.get('description')[:100]}...")
                
            assert "predicted_count" in risk_details
            assert meta.get("model_version") == "3.0.0-ECO"
            print("\nVERIFICATION SUCCESSFUL: Ecosystem model is integrated and returning data.")
        else:
            print(f"API Error: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"Connection Failed: {e}")

if __name__ == "__main__":
    test_ecosystem_api()
