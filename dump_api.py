import requests
import json

def dump():
    url = "http://localhost:8000/api/v1/species/Tiger"
    try:
        res = requests.get(url)
        data = res.json()
        print(f"EST_POP: {data['species']['estimated_population']}")
        print(f"PULSE_LATEST: {data['species']['pulse_history'][0]['count'] if data['species']['pulse_history'] else 'N/A'}")
        print(f"HIST_LATEST: {data['species']['population_history'][-1]['count'] if data['species']['population_history'] else 'N/A'}")
        # print(json.dumps(data, indent=2)) # Too big probably
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    dump()
