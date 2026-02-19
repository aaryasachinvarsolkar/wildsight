import sys
import os
import math

# Add backend to path
sys.path.append(os.path.join(os.getcwd(), 'backend'))

from app.services.geospatial import geospatial_service

def check_env(lat, lon):
    print(f"Checking Env Data for {lat}, {lon}...")
    try:
        data = geospatial_service.get_environmental_data(lat, lon)
        print(f"NDVI: {data.ndvi}")
        print(f"Temp: {data.temperature_celsius}")
        print(f"Rain: {data.rainfall_forecast_mm}")
        print(f"Fire: {data.fire_radiative_power}")
        print(f"HDI: {data.human_development_index}")
        
        # Check for NaNs
        vals = [data.ndvi, data.temperature_celsius, data.rainfall_forecast_mm, data.fire_radiative_power, data.human_development_index]
        for v in vals:
            if isinstance(v, float) and (math.isnan(v) or math.isinf(v)):
                 print("!!! FOUND NaN !!!")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    # Test with the coordinates of the failing Zone (Tiroda?)
    # Based on earlier logs: 21.15, 79.08
    check_env(21.15, 79.08)
