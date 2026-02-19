import os
from dotenv import load_dotenv
from google import genai

load_dotenv(os.path.join(os.getcwd(), 'backend', '.env'))

def list_models():
    api_key = os.getenv("GOOGLE_API_KEY")
    client = genai.Client(api_key=api_key)
    print("--- AVAILABLE MODELS ---")
    try:
        # The new SDK might have a different way to list models, or we'll just test a few
        models = ["gemini-1.5-flash", "gemini-1.5-pro", "gemini-2.0-flash-exp"]
        for m in models:
            try:
                res = client.models.generate_content(model=m, contents="hi")
                print(f"Model {m}: OK")
            except Exception as e:
                print(f"Model {m}: FAILED ({e})")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    list_models()
