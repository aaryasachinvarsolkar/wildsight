
import sys
from app.services.biometric import BiometricService

def verify():
    service = BiometricService()
    print("Service initialized.")
    
    # 1. Check if Tahr is loaded in DB
    tahr = service.species_db.get("nilgiri tahr")
    if tahr:
        print(f"DB Entry Found: Yes")
        print(f"Estimated Pop in DB: {tahr.get('estimated_population')}")
    else:
        print("DB Entry Found: No")
        
    # 2. Run calculation logic
    # Mocking inputs simulating a GBIF result of 0 or random
    result = service._calculate_scientific_error("Nilgiri Tahr", 100)
    print(f"Final Scientific Result: {result}")
    
    if result.get("estimated_true_population") == 3125:
        print("SUCCESS: Exact count retrieved from DB.")
    else:
        print("FAILURE: Logic did not use DB value.")

if __name__ == "__main__":
    verify()
