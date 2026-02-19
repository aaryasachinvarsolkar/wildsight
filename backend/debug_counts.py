from app.services.biometric import biometric_service
import json

def check_counts():
    targets = ["Tiger", "Asian Elephant"]
    for species in targets:
        print(f"\n{'='*20}")
        print(f"CHECKING: {species}")
        print(f"{'='*20}")
        
        # 1. Fetch raw data
        checkpoints, final_name, meta, species_key = biometric_service._fetch_from_gbif(species)
        total_raw = len(checkpoints)
        print(f"Total Raw Checkpoints (GBIF): {total_raw}")
        
        # 2. Run Spatial Analysis
        spatial = biometric_service._analyze_spatial_distribution(checkpoints, final_name)
        total_in_analysis = spatial.get("total_sightings")
        estimated = spatial.get("total_estimated_individuals")
        sci_context = spatial.get("scientific_context", {})
        
        print(f"Total Sightings Summed in Clusters: {total_in_analysis}")
        print(f"Estimated True Population: {estimated}")
        print(f"Scientific Context: {json.dumps(sci_context, indent=2)}")
        
        # 3. Check Zones
        zones = spatial.get("zones", [])
        print(f"Top 3 Zones:")
        for z in zones[:3]:
            print(f"  - {z['name']}: {z['sighting_count']} sightings -> {z['estimated_count']} estimated")

if __name__ == "__main__":
    check_counts()
