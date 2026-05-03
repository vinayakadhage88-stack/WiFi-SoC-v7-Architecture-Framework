"""
AI Detection Engine - Isolation Forest for Anomaly Detection
"""
from sklearn.ensemble import IsolationForest
import numpy as np


class AIEngine:
    def __init__(self):
        self.model = IsolationForest(contamination=0.1, random_state=42)
        self.trained = False
        self.training_data = []

    def train(self, data):
        """Train the anomaly detection model"""
        if len(data) > 0:
            self.model.fit(data)
            self.trained = True
            print(f"✓ AI Model trained with {len(data)} samples")

    def predict(self, data):
        """
        Predict anomalies
        Returns -1 for anomaly, 1 for normal
        """
        if not self.trained:
            # Use default training if model not trained
            default_data = np.array([
                [20, 30],  # Normal low
                [50, 50],  # Normal medium
                [40, 40],  # Normal medium-low
            ])
            self.train(default_data)
        
        return self.model.predict(data)

    def add_training_sample(self, features):
        """Add sample for training"""
        self.training_data.append(features)
        if len(self.training_data) >= 100:  # Retrain every 100 samples
            self.train(np.array(self.training_data))
            self.training_data = []
