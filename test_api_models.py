import os
from dotenv import load_dotenv
from google import genai

load_dotenv(os.path.join(os.getcwd(), 'backend', '.env'))

def test_specific_models():
    api_key = os.getenv("GOOGLE_API_KEY")
    client = genai.Client(api_key=api_key)
    print("--- MODEL CONNECTIVITY TEST ---")
    
    # Common model strings for the new SDK
    variants = [
        "gemini-1.5-flash",
        "gemini-1.5-pro",
        "gemini-2.0-flash-exp"
    ]
    
    for m in variants:
        try:
            print(f"Testing {m}...")
            res = client.models.generate_content(model=m, contents="Say 'OK'")
            print(f"  -> {m} SUCCESS: {res.text.strip()}")
        except Exception as e:
            print(f"  -> {m} FAILED: {type(e).__name__}")

if __name__ == "__main__":
    test_specific_models()
