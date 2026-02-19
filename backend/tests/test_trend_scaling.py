
import sys
import os
import time

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Mock Dependencies
from unittest.mock import MagicMock
sys.modules["google"] = MagicMock()
sys.modules["google.genai"] = MagicMock()
sys.modules["app.services.report"] = MagicMock()
sys.modules["app.models.db"] = MagicMock()
sys.modules["app.models.db"].engine = MagicMock()

try:
    from app.services.biometric import biometric_service
except ImportError as e:
    print(e)
    sys.exit(1)

def test_trend_scaling():
    print("Testing Trend Scaling Factor...")
    
    # 1. Mock _get_gbif_trend_factor to return 1.2 (+20%)
    # biometric_service._get_gbif_trend_factor = MagicMock(return_value=1.2)
    # Using real implementation might fail if no internet, but let's try calling internal methods if possible.
    
    # 2. Test Low Level _calculate_scientific_error with Baseline
    # "Tiger" has baseline 3682 in species_niches.json
    print("\n[Case 1] Tiger (Baseline 3682) with Trend 1.2 (Growth)")
    res = biometric_service._calculate_scientific_error(
        "Tiger", 
        raw_count=50, 
        trend_factor=1.2
    )
    print(f"Result: {res['estimated_true_population']}")
    
    expected = int(3682 * 1.2)
    diff = abs(res['estimated_true_population'] - expected)
    if diff < 5:
        print("SUCCESS: Count Scaled Correctly.")
    else:
        print(f"FAILURE: Expected {expected}, Got {res['estimated_true_population']}")

    print("\n[Case 2] Tiger with Trend 0.8 (Decline)")
    res_down = biometric_service._calculate_scientific_error(
        "Tiger", 
        raw_count=50, 
        trend_factor=0.8
    )
    print(f"Result: {res_down['estimated_true_population']}")
    
    expected_down = int(3682 * 0.8)
    if abs(res_down['estimated_true_population'] - expected_down) < 5:
         print("SUCCESS: Count Scaled Correctly.")
    else:
         print(f"FAILURE: Expected {expected_down}, Got {res_down['estimated_true_population']}")

if __name__ == "__main__":
    test_trend_scaling()
