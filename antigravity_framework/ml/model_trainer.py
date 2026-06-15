import os
import joblib
import numpy as np
import pandas as pd
from typing import Dict, Any, Tuple
from loguru import logger
from sklearn.ensemble import IsolationForest, RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score

class ONUModelTrainer:
    def __init__(self, model_dir: str = "./models"):
        self.model_dir = model_dir
        os.makedirs(self.model_dir, exist_ok=True)
        self.iso_forest_path = os.path.join(self.model_dir, "isolation_forest.joblib")
        self.rf_classifier_path = os.path.join(self.model_dir, "random_forest.joblib")

    def prepare_dataset(self, onu_logs: list) -> Tuple[pd.DataFrame, np.ndarray]:
        """Preprocesses raw ONU logs and generates labeled datasets."""
        # Standard dummy data generator if no logs are provided
        if not onu_logs:
            logger.info("No logs provided, generating high-quality simulated dataset.")
            # Normal data (100 samples)
            normal_data = []
            for _ in range(100):
                normal_data.append({
                    "registration_hour": np.random.randint(8, 18),
                    "optical_power": np.random.uniform(-22.0, -18.0),
                    "omci_freq": np.random.uniform(20.0, 40.0),
                    "serial_number": "HWTC" + "".join(np.random.choice(list("0123456789ABCDEF"), 8)),
                    "loid": "LOID_VNPT_" + str(np.random.randint(1000, 9999)),
                    "traffic_deviation": np.random.uniform(0.1, 1.0),
                    "port_consistent": True,
                    "rereg_freq": np.random.randint(0, 2),
                    "label": 1  # Normal
                })
            
            # Anomaly/Rogue data (15 samples)
            rogue_data = []
            for _ in range(15):
                rogue_data.append({
                    "registration_hour": np.random.choice([1, 2, 3, 23]), # unusual hours
                    "optical_power": np.random.choice([np.random.uniform(-35.0, -29.0), np.random.uniform(-5.0, -2.0)]), # anomalous power
                    "omci_freq": np.random.uniform(80.0, 150.0), # flood frequency
                    "serial_number": "FAKE" + "".join(np.random.choice(list("0123456789ABCDEF"), 8)), # rogue vendor prefix
                    "loid": "invalid-format-no-underscore",
                    "traffic_deviation": np.random.uniform(5.0, 15.0), # massive deviation
                    "port_consistent": False, # ported elsewhere
                    "rereg_freq": np.random.randint(10, 30), # flapping
                    "label": -1  # Rogue/Anomaly
                })
            
            onu_logs = normal_data + rogue_data

        # Extract features
        from antigravity_framework.ml.feature_extractor import ONUFeatureExtractor
        extractor = ONUFeatureExtractor()
        
        X = extractor.create_batch_dataset(onu_logs)
        y = np.array([log.get("label", 1) for log in onu_logs])
        
        return X, y

    def train_isolation_forest(self, X: pd.DataFrame) -> IsolationForest:
        """Trains an unsupervised Isolation Forest model to detect outliers."""
        logger.info("Training Isolation Forest model...")
        # contamination represents expected proportion of rogue ONUs (e.g. 10%)
        model = IsolationForest(n_estimators=100, contamination=0.1, random_state=42)
        model.fit(X)
        
        # Save model
        joblib.dump(model, self.iso_forest_path)
        logger.info(f"Saved Isolation Forest model to {self.iso_forest_path}")
        return model

    def train_random_forest(self, X: pd.DataFrame, y: np.ndarray) -> Tuple[RandomForestClassifier, Dict[str, Any]]:
        """Trains a supervised Random Forest Classifier if labeled data exists."""
        logger.info("Training Random Forest Classifier...")
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)
        
        model = RandomForestClassifier(n_estimators=100, random_state=42)
        model.fit(X_train, y_train)
        
        # Evaluate
        predictions = model.predict(X_test)
        accuracy = accuracy_score(y_test, predictions)
        report = classification_report(y_test, predictions, output_dict=True)
        
        logger.info(f"Random Forest Accuracy: {accuracy:.4f}")
        
        # Save model
        joblib.dump(model, self.rf_classifier_path)
        logger.info(f"Saved Random Forest model to {self.rf_classifier_path}")
        
        eval_metrics = {
            "accuracy": accuracy,
            "precision": report["macro avg"]["precision"],
            "recall": report["macro avg"]["recall"],
            "f1_score": report["macro avg"]["f1-score"]
        }
        return model, eval_metrics

    def load_models(self) -> Tuple[Any, Any]:
        """Loads models from disk if they exist."""
        iso_model = joblib.load(self.iso_forest_path) if os.path.exists(self.iso_forest_path) else None
        rf_model = joblib.load(self.rf_classifier_path) if os.path.exists(self.rf_classifier_path) else None
        return iso_model, rf_model
