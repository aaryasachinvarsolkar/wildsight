import sys
import os

# Add backend to path
sys.path.append(os.path.join(os.getcwd(), 'backend'))

from app.services.biometric import biometric_service
from app.services.report import report_service

def trace_gemini():
    print("--- TRACING GEMINI CENSUS RESPONSE ---")
    species = "Panthera tigris"
    prompt = f"""
             What is the most recent estimated total population of "{species}" in India?
             Return ONLY the integer number. 
             If exact count is unknown, return the best scientific estimate.
             If widely unknown or unavailable, return -1.
             Do not include commas or text. Just the integer.
             """
    response = report_service.client.models.generate_content(
        model='gemini-1.5-flash',
        contents=prompt
    )
    print(f"RAW RESPONSE: {response.text.strip()}")

if __name__ == "__main__":
    trace_gemini()
