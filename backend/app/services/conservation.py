from typing import List, Dict, Any, Optional
import os
import random
from datetime import datetime
from app.models.schemas import RiskAssessment, Prescription, EnvironmentalData
from app.services.report import report_service

class ConservationService:
    def recommend_actions(self, risk: RiskAssessment, h3_index: str, species_name: str, population_count: int, env_data: EnvironmentalData = None) -> List[Prescription]:
        # Rule-based priority
        priority = "critical" if risk.risk_score > 0.7 or population_count < 500 else "high"
        
        # Decide Action Type from Primary Stressor
        action_map = {
            "fire": "Forest_Fire_Monitoring",
            "drought": "Water_Hole_Construction",
            "heatwave": "Climate_Resilience_Corridor",
            "encroachment": "Anti_Poaching_Patrol",
            "habitat_loss": "Habitat_Restoration"
        }
        action_type = action_map.get(risk.primary_stressor, "General_Monitoring")
        
        description = self._generate_detailed_plan(action_type, risk, species_name, population_count, env_data)
        
        return [Prescription(
            action_type=action_type,
            priority=priority,
            target_zone_h3=h3_index or "national",
            estimated_cost=5000 * (1 + risk.risk_score),
            expected_outcome=f"Mitigates threat of {risk.primary_stressor}",
            description=description
        )]

    def _generate_detailed_plan(self, action_name: str, risk: RiskAssessment, species_name: str, population_count: int, env_data: EnvironmentalData = None) -> str:
        location_name = env_data.place_name if env_data else "this Indian habitat"
        
        prompt = f"""
        Act as a conservation expert specialized in the biodiversity of INDIA. 
        Write a concise markdown field action plan for: {species_name}.
        Location: {location_name}. Population: {population_count}.
        Threat: {risk.primary_stressor} (Risk: {risk.risk_score}).
        Action: {action_name}.
        Structure: Diagnosis, Critical Intervention, Resilience Strategy, Community Role.
        Keep it to 2-3 sentences per section. Use the location name frequently.
        """
        
        try:
            if not report_service.client: raise Exception("No Gemini")
            response = report_service.client.models.generate_content(model="gemini-1.5-flash", contents=prompt)
            return response.text
        except Exception:
            return f"""
### 1. ⚠️ Diagnosis
Analysis of **{location_name}** indicates that {species_name} is primarily threatened by **{risk.primary_stressor.replace('_', ' ')}** (Vector Intensity: {risk.risk_score}).

### 2. 🛡️ Critical Intervention
Initiate **{action_name.replace('_', ' ')}** focusing on high-risk sectors within {location_name}. This operation must counteract the environmental pressure while maintaining life-support zones.

### 3. 🌿 Resilience Strategy
Long-term stability for {species_name} in {location_name} requires addressing the root drivers of habitat stress. We recommend establishing a buffer zone around analyzed habitat.

### 4. 🤝 Community Role
Indian stakeholders in **{location_name}** are vital to the success of this conservation effort. Community-led monitoring has been proven to reduce local impacts significantly.
"""

conservation_service = ConservationService()
