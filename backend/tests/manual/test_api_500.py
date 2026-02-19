import requests
import time

def test_api():
    url = "http://localhost:8000/api/v1/species/Tiger"
    print(f"Testing {url}...")
    try:
        res = requests.get(url, timeout=30)
        print(f"Status: {res.status_code}")
        if res.status_code == 500:
            print("Response Content:")
            print(res.text)
        else:
            print("Success or non-500 error.")
    except Exception as e:
        print(f"Request Error: {e}")

if __name__ == "__main__":
    test_api()
