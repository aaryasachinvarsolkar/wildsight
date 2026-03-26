import joblib
import os

model_path = r"c:\Users\Shruti Subramanian\Downloads\wildsight\backend\app\models\risk_model.pkl"
data = joblib.load(model_path)
print(f"Keys: {data.keys()}")
for k, v in data.items():
    print(f"Key: {k}, Type: {type(v)}")
    if hasattr(v, "feature_names_in_"):
        print(f"  Features for {k}: {v.feature_names_in_}")
    elif hasattr(v, "n_features_in_"):
        print(f"  Num Features for {k}: {v.n_features_in_}")
