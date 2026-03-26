from app.services.taxonomy import taxonomy_service
from app.services.population import population_service

class BiometricService:
    def get_species_data(self, species_name: str, zone_id: str = None) -> dict:
        key, name, meta = taxonomy_service.resolve_name(species_name)
        if not key: return {}
        
        pop_data = population_service.get_population_data(name, key=key)
        
        # Merge for backward compatibility
        res = {
            "species_name": name,
            "checkpoints": pop_data["checkpoints"],
            "estimated_population": pop_data["estimated_population"],
            "population_history": pop_data["population_history"],
            "status": "Vulnerable",
            "biological_traits": meta,
            "sensitivities": {
                "fire": 0.5, "rainfall": 0.5, "temp": 0.5, "hdi": 0.5, "ndvi": 0.5
            }
        }
        return res

biometric_service = BiometricService()
