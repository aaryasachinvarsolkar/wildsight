import json
import csv
import random
import os
from pathlib import Path

def load_species_data(filepath):
    with open(filepath, 'r') as f:
        return json.load(f)

def generate_data():
    base_dir = Path(__file__).resolve().parent.parent
    json_path = base_dir / "data" / "species_niches.json"
    csv_path = base_dir / "data" / "intervention_history_v2.csv"
    
    species_list = load_species_data(json_path)
    
    # Define Knowledge Base: Sensitivity -> (Effective Actions, Ineffective Actions)
    search_space = {
        "fire": {
            "effective": ["fire_breaks", "early_warning_system", "controlled_burn"],
            "ineffective": ["fencing", "supplemental_feeding", "vaccination"]
        },
        "poaching": {
            "effective": ["anti_poaching_patrols", "drone_surveillance", "community_engagement"],
            "ineffective": ["reforestation", "water_hole_construction"]
        },
        "encroachment": {
            "effective": ["protected_zone_enforcement", "corridor_restoration", "community_fencing"],
            "ineffective": ["disease_monitoring", "supplemental_feeding"]
        },
        "drought": {
            "effective": ["water_hole_construction", "drought_resistant_planting"],
            "ineffective": ["anti_poaching_patrols", "fire_breaks"] # Not relevant to drought
        },
        "disease": {
            "effective": ["vaccination_drive", "quarantine_zone", "disease_monitoring"],
            "ineffective": ["fire_breaks", "anti_poaching_patrols"]
        },
        "power_lines": {
            "effective": ["underground_cabling", "bird_diverters"],
            "ineffective": ["reforestation", "water_hole_construction"]
        },
        "flood": {
            "effective": ["embankment_reinforcement", "high_ground_creation"],
            "ineffective": ["fencing", "controlled_burn"]
        }
    }
    
    defaults = {
        "effective": ["monitoring", "research_study"],
        "ineffective": ["relocation"] # High risk, usually bad first step
    }

    records = []
    
    print(f"Generating synthetic data for {len(species_list)} species...")
    
    for _ in range(2000): # Generate 2000 synthetic historical records
        # 1. Pick a random species context
        species = random.choice(species_list)
        sensitivities = species.get("sensitivities", {})
        
        # 2. Pick a primary stressor (Sensitivity or Random Environment Factor)
        # 70% chance we pick something the species is SENSITIVE to (Simulating a crisis event for that species)
        if sensitivities and random.random() < 0.7:
            # Weighted choice: Critical -> higher chance
            keys = list(sensitivities.keys())
            weights = [3 if sensitivities[k] == "critical" else (2 if sensitivities[k] == "high" else 1) for k in keys]
            primary_stressor = random.choices(keys, weights=weights, k=1)[0]
        else:
            # Random background stressor
            primary_stressor = random.choice(list(search_space.keys()))
            
        # 3. Determine if this species is SENSITIVE to this stressor
        sensitivity_level = sensitivities.get(primary_stressor, "none")
        is_sensitive = sensitivity_level in ["critical", "high", "medium"]
        
        # 4. Select Action
        knowledge = search_space.get(primary_stressor, defaults)
        
        # We want to train the model to succeed what works, and fail what doesn't.
        # But we also need to teach it: "If species is sensitive to X, and you treat X, it's VERY effective"
        
        if random.random() < 0.5:
            # Generate a SUCCESS case
            action = random.choice(knowledge["effective"])
            outcome = "success"
        else:
            # Generate a FAILURE case
            action = random.choice(knowledge["ineffective"])
            outcome = "failure"
            
        # 5. Calculate Score modifiers
        # Used for features.
        risk_score = random.uniform(0.3, 0.9)
        hdi = random.uniform(0.1, 0.6)
        
        # Encoding Sensitivity as a Feature
        # We will use simplified columns: [is_sensitive_fire, is_sensitive_poaching, ...] 
        # But for the CSV, we'll dump specific boolean columns for the top 5 common stressors
        
        row = {
            "species_name": species["species_name"],
            "primary_stressor": primary_stressor,
            "risk_score": round(risk_score, 2),
            "hdi": round(hdi, 2),
            "action": action,
            "outcome": outcome,
            
            # Context Features (The Model Needs These to Learn Specificity)
            "sens_fire": 1 if sensitivities.get("fire") in ["critical", "high"] else 0,
            "sens_poaching": 1 if sensitivities.get("poaching") in ["critical", "high"] else 0,
            "sens_encroachment": 1 if sensitivities.get("encroachment") in ["critical", "high"] else 0,
            "sens_drought": 1 if sensitivities.get("drought") in ["critical", "high"] else 0,
            "sens_disease": 1 if sensitivities.get("disease") in ["critical", "high"] else 0,
            "sens_power_lines": 1 if sensitivities.get("power_lines") in ["critical", "high"] else 0,
        }
        
        records.append(row)
        
    # Write to CSV
    headers = list(records[0].keys())
    with open(csv_path, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        writer.writeheader()
        writer.writerows(records)
        
    print(f"Successfully generated {len(records)} records at {csv_path}")

if __name__ == "__main__":
    generate_data()
