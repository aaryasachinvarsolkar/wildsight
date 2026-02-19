import requests
import json

def test_lookup():
    print("--- GBIF Lookup Debug ---")
    
    # 1. Match "Tiger"
    url = "https://api.gbif.org/v1/species/match"
    params = {"name": "Tiger", "strict": "false"}
    res = requests.get(url, params=params)
    print(f"\nMatch 'Tiger': {res.json().get('scientificName')} (Key: {res.json().get('usageKey')})")
    
    # 2. Search "Tiger"
    url = "https://api.gbif.org/v1/species/search"
    params = {"q": "Tiger", "limit": 20}
    res = requests.get(url, params=params)
    results = res.json().get("results", [])
    print(f"\nSearch 'Tiger' (Top 20):")
    found_panthera = False
    for r in results:
        print(f"- {r.get('scientificName')} (Key: {r.get('key')}, Class: {r.get('class')})")
        if "panthera tigris" in r.get('scientificName', '').lower():
            found_panthera = True
            
    if not found_panthera:
        print("\nWARNING: Panthera tigris NOT found in Top 20 results!")
    else:
        print("\nSUCCESS: Panthera tigris present in results.")

    # 3. Match "Panthera tigris" (Control)
    params = {"name": "Panthera tigris", "strict": "false"}
    res = requests.get("https://api.gbif.org/v1/species/match", params=params)
    print(f"\nControl Match 'Panthera tigris': {res.json().get('scientificName')} (Key: {res.json().get('usageKey')})")

if __name__ == "__main__":
    test_lookup()
