import sys
import os
import traceback

# Add backend to path
sys.path.append(os.path.join(os.getcwd(), 'backend'))

from app.services.biometric import biometric_service

def test():
    try:
        print("Testing Biometric Service for 'Bengal Tiger'...")
        data = biometric_service.get_species_data("Bengal Tiger")
        print("Result Success!")
        print(f"Species: {data.get('species_name')}")
    except Exception as e:
        print("CRASH DETECTED:")
        traceback.print_exc()

if __name__ == "__main__":
    test()
