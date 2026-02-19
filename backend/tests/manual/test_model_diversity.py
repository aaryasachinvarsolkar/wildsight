import sys
import os
import json
import h3

# Add backend to path
sys.path.append(os.path.join(os.getcwd(), "backend"))

from dotenv import load_dotenv
load_dotenv()

from app.services.intelligence import prescription_engine, RiskEstimator
from app.models.schemas import RiskAssessment, EnvironmentalData

def test_diversity():
    log_file = open("diversity_results.txt", "w")
    def log(msg):
        print(msg)
        log_file.write(str(msg) + "\n")
        
    log("=== ML DIVERSITY VERIFICATION (LEVEL 6 + DYNAMIC BIAS) ===")
    
    scenarios = [
        {
            "name": "Tiger in Heatwave (Khatia)",
            "species": "Bengal Tiger",
            "lat": 22.33, "lon": 80.61,
            "meta": {
                "biological_traits": {"class": "mammalia", "order": "carnivora"},
                "sensitivities": {"temp": "critical", "poaching": "high", "ndvi": "medium"}
            },
            "env": EnvironmentalData(
                ndvi=0.6, evi=0.55, ndwi=-0.2, temperature_celsius=46.5, 
                rainfall_forecast_mm=50, fire_radiative_power=0.0, 
                human_development_index=0.6, nightlights=6.0
            )
        },
        {
            "name": "Tiger in Forest Fire (Mukki)",
            "species": "Bengal Tiger",
            "lat": 22.20, "lon": 80.65,
            "meta": {
                "biological_traits": {"class": "mammalia", "order": "carnivora"},
                "sensitivities": {"fire": "critical", "poaching": "high", "ndvi": "medium"}
            },
            "env": EnvironmentalData(
                ndvi=0.2, evi=0.15, ndwi=0.1, temperature_celsius=38, 
                rainfall_forecast_mm=200, fire_radiative_power=180.5, 
                human_development_index=0.1, nightlights=1.0
            )
        },
        {
            "name": "GIB near Power Lines (Kutch)",
            "species": "Great Indian Bustard",
            "lat": 23.5, "lon": 69.5,
            "meta": {
                "biological_traits": {"class": "aves"},
                "sensitivities": {"power_lines": "critical", "encroachment": "high"}
            },
            "env": EnvironmentalData(
                ndvi=0.3, evi=0.25, ndwi=-0.1, temperature_celsius=32, 
                rainfall_forecast_mm=100, fire_radiative_power=0.0, 
                human_development_index=0.3, nightlights=2.0
            )
        }
    ]

    re = RiskEstimator()
    
    for s in scenarios:
        try:
            h3_res6 = h3.geo_to_h3(s['lat'], s['lon'], 6)
        except AttributeError:
            h3_res6 = h3.latlng_to_cell(s['lat'], s['lon'], 6)
            
        log(f"\nScenario: {s['name']}")
        log(f"Location: {s['lat']}, {s['lon']} (H3 Level 6: {h3_res6})")
        
        s['env'].h3_index = h3_res6
        risk = re.estimate_risk(s['env'], s['meta']['sensitivities'])
        
        log(f"Primary Stressor: {risk.primary_stressor} (Score: {risk.risk_score})")
        
        actions = prescription_engine.recommend_actions(
            risk=risk,
            h3_index=h3_res6,
            species_name=s['species'],
            species_data=s['meta'],
            env_data=s['env']
        )
        
        log("Recommendations:")
        for a in actions:
            log(f" -> [{a.priority.upper()}] {a.action_type}")
            # log(f"    Detail: {a.expected_outcome}")

    log_file.close()

if __name__ == "__main__":
    test_diversity()
