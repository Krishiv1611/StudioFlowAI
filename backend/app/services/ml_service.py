import joblib
import pandas as pd
import os
from typing import Dict, Any, List
from app.config.settings import settings
import copy

class MLService:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(MLService, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not hasattr(self, '_initialized'):
            self.virality_model = None
            self.virality_metadata = None
            self.reach_model = None
            self.reach_metadata = None
            self._load_virality_model()
            self._load_reach_model()
            self._initialized = True

    def _load_virality_model(self):
        try:
            model_path = os.path.join(settings.BASE_DIR, 'ml', 'models', 'virality_model.pkl')
            meta_path = os.path.join(settings.BASE_DIR, 'ml', 'models', 'model_metadata.pkl')
            if os.path.exists(model_path):
                self.virality_model = joblib.load(model_path)
                self.virality_metadata = joblib.load(meta_path)
                print(f"Virality Model Loaded. Threshold: {self.virality_metadata.get('viral_threshold_value')}")
            else:
                print("Virality Model not found at", model_path)
        except Exception as e:
            print(f"Error loading Virality Model: {e}")

    def _load_reach_model(self):
        try:
            model_path = os.path.join(settings.BASE_DIR, 'ml', 'models', 'reach_model.pkl')
            meta_path = os.path.join(settings.BASE_DIR, 'ml', 'models', 'reach_metadata.pkl')
            if os.path.exists(model_path):
                self.reach_model = joblib.load(model_path)
                self.reach_metadata = joblib.load(meta_path)
                print("Reach Prediction Model Loaded.")
            else:
                print("Reach Model not found.")
        except Exception as e:
            print(f"Error loading Reach Model: {e}")

    def predict_virality(self, features: dict) -> float:
        """
        Predicts virality score (probability of being viral).
        """
        if not self.virality_model:
            return 0.5 
        try:
            df = pd.DataFrame([features])
            proba = self.virality_model.predict_proba(df)[:, 1][0]
            return float(proba)
        except Exception as e:
            print(f"Prediction Error: {e}")
            return 0.0

    def predict_reach(self, features: dict) -> float:
        """
        Predicts estimated impressions (Reach).
        """
        if not self.reach_model:
            return 0.0
        
        try:
            df = pd.DataFrame([features])
            prediction = self.reach_model.predict(df)[0]
            return max(0.0, float(prediction))
        except Exception as e:
            print(f"Reach Prediction Error: {e}")
            return 0.0

    def recommend_schedule(self, base_features: dict) -> list:
        """
        Predicts the best time and day to post by simulating all possibilities.
        """
        if not self.reach_model:
            return []

        days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        hours = [9, 12, 15, 18, 21] 
        
        predictions = []
        
        for day in days:
            for hour in hours:
                test_feat = copy.deepcopy(base_features)
                test_feat['day_of_week'] = day
                test_feat['hour_of_day'] = hour
                
                # Ensure follower_count is present if model expects it
                if 'follower_count' not in test_feat:
                     test_feat['follower_count'] = 0

                reach = self.predict_reach(test_feat)
                
                predictions.append({
                    "day": day,
                    "hour": hour,
                    "predicted_reach": reach
                })

        predictions.sort(key=lambda x: x['predicted_reach'], reverse=True)
        return predictions[:3]
