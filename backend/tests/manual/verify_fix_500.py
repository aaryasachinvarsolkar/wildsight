import requests
import time

def check_health():
    url = "http://localhost:8000/api/v1/species/Tiger"
    print(f"Checking {url}...")
    try:
        # Retry logic because server might be warming up
        for i in range(5):
            try:
                res = requests.get(url, timeout=5)
                if res.status_code == 200:
                    print("SUCCESS: Server responded with 200 OK.")
                    print(f"Data keys: {list(res.json().keys())}")
                    return
                else:
                    print(f"Server returned {res.status_code}: {res.text[:100]}")
            except requests.exceptions.ConnectionError:
                print("Server not ready yet, retrying...")
            time.sleep(2)
        print("FAIL: Server did not respond in time.")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_health()
