
print("start")
try:
    import sys
    print("sys ok")
    import os
    print("os ok")
    from sklearn.ensemble import RandomForestRegressor
    print("sklearn ok")
    from google import genai
    print("google.genai ok")
    from app.models.schemas import RiskAssessment
    print("schemas ok")
except Exception as e:
    print(f"ERROR: {e}")
except ImportError as e:
    print(f"IMPORT ERROR: {e}")
print("done")
