import requests
import json
import time

def test_history():
    species = "Tiger"
    url = f"http://localhost:8000/api/v1/species/{species}"
    
    print(f"Testing {url}...")
    try:
        start = time.time()
        res = requests.get(url, timeout=30)
        duration = time.time() - start
        
        if res.status_code == 200:
            data = res.json()
            species_data = data['species']
            
            # 1. Check Population Trend (Vulnerability Graph)
            years = species_data.get('years', [])
            pop_hist = species_data.get('population_history', [])
            print(f"--- Population Trend ---")
            print(f"Years: {years}")
            print(f"Data Points: {len(pop_hist)}")
            
            # Anchor Check
            est_pop = species_data.get('estimated_population')
            last_point = pop_hist[-1]['count'] if pop_hist else 0
            
            print(f"Estimated Pop (Card): {est_pop}")
            print(f"Trend 2025 (Graph): {last_point}")
            
            if abs(est_pop - last_point) < 5: # Allow small int rounding diff
                print("SUCCESS: Graph is strictly anchored to Current Count.")
            else:
                 print(f"FAILURE: Graph mismatch. {est_pop} vs {last_point}")

            if len(years) == len(pop_hist) == 5:
                print(f"SUCCESS: Population data synchronized. Range: {years[0]} - {years[-1]}")

            # 2. Check Habitat Analytics Labels
            labels = species_data.get('years_history', [])
            print(f"--- Habitat Analytics ---")
            print(f"Labels (dates): {len(labels)}")
            if any("-" in str(label) for label in labels):
                print(f"SUCCESS: Date strings detected: {labels[0]}")
            else:
                print(f"WARN: No date strings in habitat labels. Got: {labels}")
            
            # 3. Check Pulse History (Monitoring Log)
            pulse = species_data.get('pulse_history', [])
            print(f"--- Monitoring Log ---")
            print(f"Pulse Points: {len(pulse)}")
            if len(pulse) > 0:
                print(f"SUCCESS: Monitoring log populated. Latest: {pulse[0]['date']} (Count: {pulse[0]['count']})")
            else:
                print("FAILURE: Monitoring log is empty.")

        else:
            print(f"API Error: {res.status_code}")
    except Exception as e:
        print(f"Connection Failed: {e}")

if __name__ == "__main__":
    test_history()
