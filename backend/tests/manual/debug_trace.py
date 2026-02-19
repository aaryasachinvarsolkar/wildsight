import sys
import os
import traceback

# Add backend to path
sys.path.append(os.path.join(os.getcwd(), 'backend'))

from app.services.biometric import biometric_service
from app.services.geospatial import geospatial_service
from app.services.intelligence import trend_analyzer, climate_predictor

def test_trace():
    print("--- Testing Full Intelligence Trace ---")
    try:
        # 1. Biometric
        print("1. Biometric...")
        bio = biometric_service.get_species_data("Tiger", zone_id="8928308280fffff")
        
        # 2. Geospatial
        print("2. Geospatial...")
        lat = 21.15
        lon = 79.08
        env = geospatial_service.get_environmental_data(lat, lon)
        
        # 3. Trend Analyzer
        print("3. Trend Analyzer...")
        trends = trend_analyzer.simulate_history(env)
        print(f"Trends: {trends.keys()}")

        # 4. Climate Predictor
        print("4. Climate Predictor...")
        climate = climate_predictor.predict_future_scenario(env, stressor="drought")
        print(f"Climate: {climate.keys()}")
        
        # 5. Deep NaN Scan
        import math
        def has_nan(obj, path=""):
            if isinstance(obj, dict):
                for k, v in obj.items():
                    has_nan(v, f"{path}.{k}")
            elif isinstance(obj, list):
                for i, v in enumerate(obj):
                    has_nan(v, f"{path}[{i}]")
            elif isinstance(obj, float):
                if math.isnan(obj) or math.isinf(obj):
                     print(f"!!! FOUND NaN at {path} = {obj} !!!")
        
        print("Scanning outputs for NaN...")
        has_nan(bio, "bio")
        has_nan(trends, "trends")
        has_nan(climate, "climate")
        
        print("Success! Trace complete.")
        
    except Exception:
        traceback.print_exc()

if __name__ == "__main__":
    test_trace()
