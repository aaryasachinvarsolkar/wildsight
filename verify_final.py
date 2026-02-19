import requests
import json

def verify_all():
    url = "http://localhost:8000/api/v1/species/Tiger"
    print(f"Verifying {url}...")
    try:
        res = requests.get(url)
        data = res.json()
        
        pop = data['species']['estimated_population']
        print(f"POPULATION: {pop}")
        
        plan = data.get('conservation_plan', [])
        print(f"PLAN ITEMS: {len(plan)}")
        
        for i, item in enumerate(plan):
            desc = item.get('description', '')
            print(f"--- Suggestion {i+1} ---")
            # Check for environmental keywords that prove location-awareness
            has_context = any(kw in desc.upper() for kw in ["NDVI", "TEMPERATURE", "RAINFALL", "HABITAT METRICS", "CERN"]) # CERN? No, TEMP.
            print(f"LOCATION-AWARE: {'YES' if has_context else 'NO'}")
            # print(f"DESC: {desc[:100]}...")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    verify_all()
