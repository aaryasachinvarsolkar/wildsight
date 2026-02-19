import requests
import json
import time

def verify():
    url = "http://localhost:8000/api/v1/species/Tiger"
    print(f"Connecting to {url}...")
    try:
        # Retry logic just in case backend is warming up
        for i in range(5):
            try:
                res = requests.get(url, timeout=5)
                if res.status_code == 200:
                    data = res.json()
                    count = data['species']['estimated_population']
                    print(f"SUCCESS: Status 200")
                    print(f"COUNT: {count}")
                    return
                else:
                    print(f"Status: {res.status_code}")
            except Exception as e:
                print(f"Attempt {i+1} failed: {e}")
            time.sleep(2)
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    verify()
