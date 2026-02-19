import sys
import os

# Add backend to path
sys.path.append(os.path.join(os.getcwd(), 'backend'))

from app.services.biometric import biometric_service
import json

def debug_tiger():
    print("--- DEBUGGING TIGER POPULATION ---")
    data = biometric_service.get_species_data("Panthera tigris")
    print(f"Species: {data['species_name']}")
    print(f"IUCN Status: {data['status']}")
    print(f"Final Estimated Population: {data['estimated_population']}")
    
    # Check spatial distribution
    dist = data['distribution_analysis']
    print(f"Total Sightings: {dist.get('total_sightings')}")
    print(f"Total Estimated Individuals (Spatial): {dist.get('total_estimated_individuals')}")
    
    # Check scientific model details
    sci = dist.get('scientific_context', {})
    print(f"ID Error Rate: {sci.get('id_error_rate')}")
    print(f"Bias Multiplier (Scaling Factor): {sci.get('scaling_factor')}")
    print(f"Research Grade Count: {sci.get('research_grade_count')}")
    
    # Check Pulse History
    pulse = data.get('pulse_history', [])
    if pulse:
        print(f"Pulse Latest Count: {pulse[0]['count']}")
    else:
        print("Pulse History: Empty")

if __name__ == "__main__":
    debug_tiger()
