import pandas as pd
import numpy as np
import pickle
import os
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report

# Paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# START CHANGE: Use Augmented Data
DATA_PATH = os.path.join(BASE_DIR, "data", "intervention_history_augmented.csv")
# END CHANGE
MODEL_PATH = os.path.join(BASE_DIR, "models", "risk_model.pkl")

class MLTrainer:
    def __init__(self):
        self.model = RandomForestClassifier(n_estimators=100, random_state=42)
        # We need encodings for inputs (stressors) and outputs (actions)
        self.stressor_encoder = LabelEncoder()
        self.action_encoder = LabelEncoder()
        
    def train_action_model(self):
        """
        Trains a classifier to predict the best Action given Risk + Context.
        Uses the Augmented Dataset for 100% coverage of archetypes.
        """
        print(f"Loading data from {DATA_PATH}...")
        try:
            df = pd.read_csv(DATA_PATH)
        except FileNotFoundError:
            print(f"Error: Data file not found at {DATA_PATH}. Please run generate_data.py first.")
            return

        # 1. Filter for Success (We only want to learn what works)
        success_df = df[df['outcome'] == 'success'].copy()
        
        if success_df.empty:
            print("Error: No successful interventions found in data.")
            return

        # 2. Prepare Features
        # Defines the "World View" of the model
        feature_cols = [
            'risk_score', 'hdi', 'ndvi', 'evi', 'ndwi', 'temp', 'rain', 'nightlights',
            'curr_fire_risk', 'curr_poaching_risk', 'curr_encroachment_risk', 
            'curr_drought_risk', 'curr_heat_risk',
            'sens_fire', 'sens_poaching', 'sens_encroachment', 
            'sens_drought', 'sens_disease', 'sens_power_lines',
            'is_plant', 'is_mammal', 'is_bird', 'is_reptile', 
            'is_amphibian', 'is_insect', 'is_marine', 'is_fungi'
        ]
        
        # Ensure columns exist (handling legacy CSVs if mixed)
        for col in feature_cols:
            if col not in success_df.columns:
                success_df[col] = 0
        
        X = success_df[feature_cols]
        y = self.action_encoder.fit_transform(success_df['action'])
        
        # 3. Train
        print(f"Training Action Model on {len(success_df)} successful scenarios...")
        
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        self.model.fit(X_train, y_train)
        
        # 4. Evaluate
        preds = self.model.predict(X_test)
        acc = accuracy_score(y_test, preds)
        print(f"Model Accuracy: {acc:.2f}")
        
        # 5. Save Artifacts
        save_dict = {
            "model": self.model,
            "action_encoder": self.action_encoder,
            "feature_cols": feature_cols
        }
        
        # Ensure model directory exists
        os.makedirs(os.path.dirname(MODEL_PATH), exist_ok=True)
        
        with open(MODEL_PATH, "wb") as f:
            pickle.dump(save_dict, f)
        print(f"Model saved to {MODEL_PATH}")

    def update_and_retrain(self, new_logs: list):
        """
        [Phase 3 Continuous Learning]
        Accepts a list of dictionaries (Pulse Logs), appends them to the dataset,
        and triggers a full retrain.
        """
        if not new_logs:
            print("No new logs to learn from.")
            return

        print(f"Incremental Learning: Ingesting {len(new_logs)} new samples...")
        
        # 1. Convert to DataFrame
        new_df = pd.DataFrame(new_logs)
        
        # 2. Append to Main Dataset
        # Ensure we have the file
        if os.path.exists(DATA_PATH):
             main_df = pd.read_csv(DATA_PATH)
             combined_df = pd.concat([main_df, new_df], ignore_index=True)
        else:
             combined_df = new_df
             
        # 3. Save Updated Dataset
        combined_df.to_csv(DATA_PATH, index=False)
        print(f"Dataset updated. Total samples: {len(combined_df)}")
        
        # 4. Retrain Model
        print("Triggering Retrain...")
        self.train_action_model()

if __name__ == "__main__":
    trainer = MLTrainer()
    trainer.train_action_model()
