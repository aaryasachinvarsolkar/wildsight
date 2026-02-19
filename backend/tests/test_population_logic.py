
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.services.biometric import BiometricService
from app.services.geospatial import geospatial_service
import unittest
from unittest.mock import MagicMock

class TestPopulationLogic(unittest.TestCase):
    def setUp(self):
        self.service = BiometricService()

    def test_calculate_scientific_error_ndvi_impact(self):
        # Case 1: Low NDVI (Barren) -> Should have lower multiplier (easier to see)
        res_low = self.service._calculate_scientific_error(
            "Testus testus", 
            raw_count=100, 
            status="Vulnerable", 
            taxonomy={"class": "Mammalia"},
            habitat_quality=0.2
        )
        
        # Case 2: High NDVI (Dense) -> Should have higher multiplier (harder to see)
        res_high = self.service._calculate_scientific_error(
            "Testus testus", 
            raw_count=100, 
            status="Vulnerable", 
            taxonomy={"class": "Mammalia"},
            habitat_quality=0.8
        )
        
        print(f"Low NDVI Pop Est: {res_low['estimated_true_population']}")
        print(f"High NDVI Pop Est: {res_high['estimated_true_population']}")
        
        self.assertLess(res_low['estimated_true_population'], res_high['estimated_true_population'], "Higher NDVI should result in higher population estimate (due to occlusion factor)")
        
    def test_integration_flow(self):
        # Mock geospatial to return fixed NDVI
        geospatial_service.get_ndvi_data = MagicMock(return_value=0.7)
        geospatial_service.get_place_name = MagicMock(return_value="Test Zone")
        
        checkpoints = [{"lat": 20.0, "lon": 78.0}, {"lat": 20.1, "lon": 78.1}] # 2 sightings
        
        result = self.service._analyze_spatial_distribution(
            checkpoints, 
            species_name="Panthera tigris", 
            status="Endangered",
            taxonomy={"class": "Mammalia", "order": "Carnivora"}
        )
        
        print(f"Resulting Population: {result['total_estimated_individuals']}")
        self.assertTrue(result['total_estimated_individuals'] > 2, "Population should be estimated > sighting count")
        
if __name__ == '__main__':
    unittest.main()
