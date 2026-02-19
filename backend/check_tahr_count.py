
import os
import sys
from dotenv import load_dotenv
from google import genai

# Load env vars
load_dotenv(dotenv_path="backend/.env")

api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    # Try VITE_GEMINI_API_KEY if main one missing
    api_key = os.getenv("VITE_GEMINI_API_KEY")

print(f"DEBUG: API Key loaded: {'Yes' if api_key else 'No'}")

client = genai.Client(api_key=api_key, http_options={'api_version': 'v1beta'})

def fetch_census_from_llm(species_name: str) -> int:
    try:
         prompt = f"""
         You are a data extraction engine.
         Context: Scientific Census Data for "{species_name}" in INDIA.
         
         Task: Return a Valid JSON object with the latest known population count.
         Format: {{"count": <integer>, "year": <integer>, "source": "<string>"}}
         
         Rules:
         - If exact count unknown, provide the best scientific estimate.
         - If species is Nilgiri Tahr, ensure you search for the 2024/2025 census data explicitly (approx 3100).
         - Return ONLY the JSON.
         """
         
         response = client.models.generate_content(
            model='gemini-1.5-flash',
            contents=prompt,
            config={'response_mime_type': 'application/json'}
         )
         
         import json
         data = json.loads(response.text)
         return int(data.get("count", -1))
    except Exception as e:
         import traceback
         traceback.print_exc()
         print(f"AI Census Fetch Error: {e}")
         return -1

count = fetch_census_from_llm("Nilgiri Tahr")
print(f"App likely showing: {count}")
