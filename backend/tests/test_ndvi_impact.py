
import sys
import os
from unittest.mock import MagicMock

# Mock Dependencies
sys.modules["google"] = MagicMock()
sys.modules["google.genai"] = MagicMock()
sys.modules["app.services.report"] = MagicMock()
sys.modules["app.models.db"] = MagicMock()
sys.modules["app.models.db"].engine = MagicMock()

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.services.biometric import biometric_service

def test_ndvi_impact():
    print("Testing NDVI Carrying Capacity Logic...")
    
    # Tiger Baseline is 3682. Ideal NDVI ~0.7.
    baseline = 3682
    
    print(f"\nBaseline: {baseline}")
    
    # Case 1: Bad Day (Drought/Fire) - NDVI 0.3
    res_bad = biometric_service._calculate_scientific_error(
        "Tiger", 
        raw_count=0, 
        trend_factor=1.0, 
        habitat_quality=0.3
    )
    count_bad = res_bad['estimated_true_population']
    print(f"Scenario: NDVI 0.3 (Degraded) -> Count: {count_bad}")
    
    # Expected: 0.3 / 0.7 = 0.42. Clamped to 0.5.
    # Count ~ 3682 * 0.5 = 1841.
    
    if count_bad < baseline:
        print("SUCCESS: Population reduced due to poor environment.")
    else:
        print("FAILURE: Population did not drop.")

    # Case 2: Good Day - NDVI 0.8
    res_good = biometric_service._calculate_scientific_error(
        "Tiger", 
        raw_count=0, 
        trend_factor=1.0, 
        habitat_quality=0.8
    )
    count_good = res_good['estimated_true_population']
    print(f"Scenario: NDVI 0.8 (Lush) -> Count: {count_good}")
    
    # Expected: 0.8 / 0.7 = 1.14.
    # Count ~ 3682 * 1.14 = 4197.
    
    if count_good > baseline:
         print("SUCCESS: Population healthy due to good environment.")
    else:
         print("FAILURE: Population did not rise.")

if __name__ == "__main__":
    test_ndvi_impact()
