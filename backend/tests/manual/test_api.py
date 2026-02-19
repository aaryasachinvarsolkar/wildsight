import requests
import json

def test():
    try:
        res = requests.get('http://localhost:8000/api/v1/species/Tiger')
        data = res.json()
        
        species = data.get("species", {})
        pulse = species.get("pulse_history", [])
        
        print(f"Species: {species.get('species_name')}")
        print(f"Pulse History Count: {len(pulse)}")
        if pulse:
            print(f"Latest Pulse: {pulse[0]}")
        else:
            print("Pulse history is empty in the API response.")
            
    except Exception as e:
        print(f"Test Failed: {e}")

if __name__ == "__main__":
    test()
