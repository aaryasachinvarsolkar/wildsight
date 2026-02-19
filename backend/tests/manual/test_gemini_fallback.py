import sys
import os
from unittest.mock import MagicMock

# Add backend to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from app.services.intelligence import prescription_engine
from app.models.schemas import RiskAssessment

def test_fallback():
    print("Testing Gemini Fallback Mechanism...")
    
    # 1. Setup mock data
    mock_risk = RiskAssessment(
        risk_score=0.8,
        primary_stressor="drought",
        anomaly_detected=True,
        details={"drought_sens": 0.8}
    )
    
    mock_species_data = {
        "biological_traits": {"class": "Mammalia"},
        "estimated_population": 500
    }
    
    # 2. Force Exception by mocking client
    original_client = prescription_engine.client
    mock_client = MagicMock()
    mock_client.models.generate_content.side_effect = Exception("429 RESOURCE_EXHAUSTED: Quota exceeded")
    prescription_engine.client = mock_client
    
    try:
        # 3. Trigger plan generation for an action in FALLBACK_PLANS
        action = "Water Hole Construction"
        print(f"Generating plan for: {action}")
        plan = prescription_engine._generate_detailed_plan(
            action_name=action,
            risk=mock_risk,
            species_name="Tiger",
            species_data=mock_species_data,
            population_count=500,
            confidence=0.9
        )
        
        # 4. Assertions
        assert "high-reliability plan" in plan, "Plan does not contain fallback indicator"
        assert "⚠️ Diagnosis" in plan, "Plan is missing structure"
        assert "Water scarcity" in plan, "Plan content looks incorrect"
        
        print("\nSUCCESS: Fallback plan correctly returned for 'Water Hole Construction'")
        print("-" * 50)
        print(plan[:200] + "...")
        print("-" * 50)

        # 5. Test unknown action fallback
        action_unknown = "Unknown Action"
        print(f"\nGenerating plan for: {action_unknown}")
        plan_unknown = prescription_engine._generate_detailed_plan(
            action_name=action_unknown,
            risk=mock_risk,
            species_name="Tiger",
            species_data=mock_species_data,
            population_count=500,
            confidence=0.9
        )
        assert "Detailed plan generation failed" in plan_unknown
        print("SUCCESS: Correctly handled missing fallback for unknown action.")

    finally:
        # Restore client
        prescription_engine.client = original_client

if __name__ == "__main__":
    test_fallback()
