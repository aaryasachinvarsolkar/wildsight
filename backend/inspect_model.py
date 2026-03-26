import pickle
import joblib
import sys
import os

model_path = r"c:\Users\Shruti Subramanian\Downloads\wildsight\backend\app\models\risk_model.pkl"

if not os.path.exists(model_path):
    print("Model not found at path.")
    sys.exit(1)

try:
    model = joblib.load(model_path)
    print(f"Model Type: {type(model)}")
    if hasattr(model, "feature_names_in_"):
        print(f"Features: {model.feature_names_in_}")
    elif hasattr(model, "n_features_in_"):
        print(f"Num Features: {model.n_features_in_}")
    
    # Try to see classes if it's a classifier
    if hasattr(model, "classes_"):
        print(f"Classes: {model.classes_}")
except Exception as e:
    print(f"Error loading model: {e}")
