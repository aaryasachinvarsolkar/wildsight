from app.services.intelligence import risk_estimator
import asyncio

async def test_future_risk():
    print("Testing ML Future Risk Predictor...")
    
    # 1. Mock Data (Negative Slope)
    hist = [{"year": "2021", "count": 100}, {"year": "2025", "count": 50}]
    climate = {"temp": [25, 30, 35]} # High volatility
    
    res = risk_estimator.predict_future_risk(hist, climate)
    print(f"Prediction (Decline): {res}")
    
    # 2. Mock Data (Positive Slope)
    hist2 = [{"year": "2021", "count": 100}, {"year": "2025", "count": 120}]
    climate2 = {"temp": [25, 26, 25]} # Stable
    
    res2 = risk_estimator.predict_future_risk(hist2, climate2)
    print(f"Prediction (Stable): {res2}")
    
    assert res["verdict"] in ["Vulnerable", "Critically Endangered"]
    assert res2["verdict"] == "Stable"
    print("SUCCESS: ML Logic Verified.")

if __name__ == "__main__":
    asyncio.run(test_future_risk())
