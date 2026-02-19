import requests
import time

def test_latency(species="Tiger"):
    url = f"http://localhost:8000/api/v1/species/{species}"
    print(f"--- Testing Latency for {species} ---")
    
    # First Run
    start = time.time()
    res = requests.get(url, timeout=30)
    dur = time.time() - start
    print(f"Run 1: {dur:.2f}s (Status: {res.status_code})")
    
    # Second Run (Should be cached)
    start = time.time()
    res = requests.get(url, timeout=30)
    dur = time.time() - start
    print(f"Run 2 (Cache): {dur:.2f}s (Status: {res.status_code})")
    print("-" * 30)

if __name__ == "__main__":
    test_latency("Bengal Tiger")
    test_latency("Indian Elephant")
