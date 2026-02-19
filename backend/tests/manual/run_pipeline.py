import sys
import os
import time

# Add backend to path
sys.path.append(os.path.join(os.getcwd(), 'backend'))

from backend.scheduler import run_pulse

def main():
    print("--- Starting WildSight Continuous Learning Pipeline ---")
    print("Mode: Automated Monitoring & Retraining")
    
    # In production, this would be a while(True) loop
    # For demo, we run it ONCE to show the effect
    try:
        run_pulse()
        print("\n[SUCCESS] Pipeline executed successfully.")
        print(" > New data fetched from Sentinel & GBIF.")
        print(" > Risk models updated/retrained.")
    except Exception as e:
        print(f"\n[ERROR] Pipeline Failed: {e}")

if __name__ == "__main__":
    main()
