import pandas as pd
import random
import os

# Define the "Knowledge Base" of Archetypes
SPECIES_ARCHETYPES = [
    # --- MAMMALS (CARNIVORES) ---
    {"class": "mammalia", "order": "carnivora", "stressor": "poaching", "action": "Intelligence_Led_Anti_Poaching", "outcome": "success"},
    {"class": "mammalia", "order": "carnivora", "stressor": "encroachment", "action": "Buffer_Zone_Enforcement", "outcome": "success"},
    {"class": "mammalia", "order": "carnivora", "stressor": "habitat_loss", "action": "Apex_Prey_Base_Restoration", "outcome": "success"},
    {"class": "mammalia", "order": "carnivora", "stressor": "fire", "action": "Fire_Refuge_Creation", "outcome": "success"},
    {"class": "mammalia", "order": "carnivora", "stressor": "heatwave", "action": "Managed_Water_Points", "outcome": "success"},

    # --- MAMMALS (MEGA-HERBIVORES) ---
    {"class": "mammalia", "order": "proboscidea", "stressor": "encroachment", "action": "Elephant_Corridor_Securitization", "outcome": "success"},
    {"class": "mammalia", "order": "proboscidea", "stressor": "drought", "action": "Solar_Pump_Water_Holes", "outcome": "success"},
    
    # --- BIRDS ---
    {"class": "aves", "stressor": "power_lines", "action": "Install_Bird_Diverters", "outcome": "success"},
    {"class": "aves", "stressor": "encroachment", "action": "Nesting_Site_Exclusion_Zones", "outcome": "success"},
    {"class": "aves", "stressor": "habitat_loss", "action": "Native_Tree_Reforestation", "outcome": "success"},
    {"class": "aves", "stressor": "pesticides", "action": "Vulture_Safe_Zone_Demarcation", "outcome": "success"},

    # --- AMPHIBIANS ---
    {"class": "amphibia", "stressor": "drought", "action": "Construct_Artificial_Wetlands", "outcome": "success"},
    {"class": "amphibia", "stressor": "disease", "action": "Fungal_Infection_Screening", "outcome": "success"},

    # --- REPTILES ---
    {"class": "reptilia", "stressor": "temperature", "action": "Micro_Thermal_Shelter_Creation", "outcome": "success"},

    # --- PLANTS ---
    {"kingdom": "plantae", "stressor": "fire", "action": "Strategic_Fire_Break_Maintenance", "outcome": "success"},
]

def generate_data(num_samples=10000):
    data = []
    
    for _ in range(num_samples):
        arc = random.choice(SPECIES_ARCHETYPES)
        
        # 1. Environmental Features
        ndvi = random.uniform(0.1, 0.9)
        evi = ndvi * random.uniform(0.8, 1.0)
        ndwi = random.uniform(-0.5, 0.5)
        temp = random.uniform(15, 45)
        rain = random.uniform(0, 3000)
        hdi = random.uniform(0.1, 0.9)
        nightlights = hdi * 10.0 + random.uniform(-1.5, 1.5)
        nightlights = max(0.0, min(10.0, nightlights))
        
        # 2. Dynamic Risk Vectors (Real-time Intensity)
        # This is the "signal" that should overwhelm static sensitivities
        curr_fire_risk = 0.0
        curr_poaching_risk = 0.0
        curr_encroachment_risk = 0.0
        curr_drought_risk = 0.0
        curr_heat_risk = 0.0
        
        if arc["stressor"] == "fire":
            curr_fire_risk = random.uniform(0.7, 1.0)
            temp = random.uniform(35, 50)
            ndvi = random.uniform(0.1, 0.4)
        elif arc["stressor"] == "poaching":
            curr_poaching_risk = random.uniform(0.7, 1.0)
        elif arc["stressor"] == "encroachment":
            curr_encroachment_risk = random.uniform(0.7, 1.0)
            hdi = random.uniform(0.6, 0.9)
        elif arc["stressor"] == "drought":
            curr_drought_risk = random.uniform(0.7, 1.0)
            rain = random.uniform(0, 300)
            ndwi = random.uniform(-0.6, -0.2)
        elif arc["stressor"] == "heatwave" or arc["stressor"] == "temperature":
            curr_heat_risk = random.uniform(0.7, 1.0)
            temp = random.uniform(38, 48)
            
        # Add background noise to other vectors
        curr_fire_risk = max(curr_fire_risk, random.uniform(0, 0.3))
        curr_poaching_risk = max(curr_poaching_risk, random.uniform(0, 0.3))
        curr_encroachment_risk = max(curr_encroachment_risk, random.uniform(0, 0.3))
        curr_drought_risk = max(curr_drought_risk, random.uniform(0, 0.3))
        curr_heat_risk = max(curr_heat_risk, random.uniform(0, 0.3))

        # 3. Static Sensitivities (Biological Traits)
        # For training, we mix these up so the model doesn't overfit
        sens_fire = 1.0 if arc["stressor"] == "fire" else random.uniform(0, 1.0)
        sens_poaching = 1.0 if arc["stressor"] == "poaching" else random.uniform(0, 1.0)
        sens_encroachment = 1.0 if arc["stressor"] == "encroachment" else random.uniform(0, 1.0)
        sens_drought = 1.0 if arc["stressor"] == "drought" else random.uniform(0, 1.0)
        sens_disease = 1.0 if arc["stressor"] == "disease" else random.uniform(0, 0.5)
        sens_power_lines = 1.0 if arc["stressor"] == "power_lines" else random.uniform(0, 0.2)

        # 4. Biological Flags
        is_plant = 1 if arc.get("kingdom") == "plantae" else 0
        is_mammal = 1 if arc.get("class") == "mammalia" else 0
        is_bird = 1 if arc.get("class") == "aves" else 0
        is_reptile = 1 if arc.get("class") == "reptilia" else 0
        is_amphibian = 1 if arc.get("class") == "amphibia" else 0
        is_insect = 1 if arc.get("class") == "insecta" else 0
        is_marine = 0
        is_fungi = 0
        
        risk_score = (curr_poaching_risk * 0.4 + curr_drought_risk * 0.3 + curr_fire_risk * 0.3)
        risk_score = max(0.0, min(1.0, risk_score))

        sample = {
            "risk_score": round(risk_score, 2),
            "hdi": round(hdi, 2), "ndvi": round(ndvi, 2), "evi": round(evi, 2),
            "ndwi": round(ndwi, 2), "temp": round(temp, 1), "rain": round(rain, 0),
            "nightlights": round(nightlights, 1),
            
            # Dynamic Vectors
            "curr_fire_risk": round(curr_fire_risk, 2),
            "curr_poaching_risk": round(curr_poaching_risk, 2),
            "curr_encroachment_risk": round(curr_encroachment_risk, 2),
            "curr_drought_risk": round(curr_drought_risk, 2),
            "curr_heat_risk": round(curr_heat_risk, 2),
            
            # Static Sensitivities
            "sens_fire": round(sens_fire, 2), "sens_poaching": round(sens_poaching, 2),
            "sens_encroachment": round(sens_encroachment, 2), "sens_drought": round(sens_drought, 2),
            "sens_disease": round(sens_disease, 2), "sens_power_lines": round(sens_power_lines, 2),
            
            # Taxonomy
            "is_plant": is_plant, "is_mammal": is_mammal, "is_bird": is_bird,
            "is_reptile": is_reptile, "is_amphibian": is_amphibian, "is_insect": is_insect,
            "is_marine": is_marine, "is_fungi": is_fungi,
            
            # Target
            "action": arc["action"],
            "outcome": "success"
        }
        data.append(sample)

    df = pd.DataFrame(data)
    output_path = os.path.join(os.path.dirname(__file__), "app", "data", "intervention_history_augmented.csv")
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    df.to_csv(output_path, index=False)
    print(f"Generated {num_samples} records to {output_path}")

if __name__ == "__main__":
    generate_data()
