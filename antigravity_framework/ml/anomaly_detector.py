import os
from typing import Dict, Any, List
from loguru import logger
from antigravity_framework.ml.feature_extractor import ONUFeatureExtractor
from antigravity_framework.ml.model_trainer import ONUModelTrainer

class AnomalyResult:
    def __init__(self, onu_id: str, score: float, label: str, reasons: List[str], action: str):
        self.onu_id = onu_id
        self.score = score               # 0.0 (normal) to 1.0 (malicious/rogue)
        self.label = label               # NORMAL, SUSPICIOUS, FAKE
        self.reasons = reasons           # List of anomalous features
        self.recommended_action = action

    def to_dict(self) -> Dict[str, Any]:
        return {
            "onu_id": self.onu_id,
            "anomaly_score": self.score,
            "label": self.label,
            "reasons": self.reasons,
            "recommended_action": self.recommended_action
        }

class ONUAnomalyDetector:
    def __init__(self, model_dir: str = "./models"):
        self.extractor = ONUFeatureExtractor()
        self.trainer = ONUModelTrainer(model_dir)
        self.iso_model, self.rf_model = self.load_or_train_default()

    def load_or_train_default(self):
        """Loads models from disk or trains defaults on demand if not found."""
        try:
            iso, rf = self.trainer.load_models()
            if iso is None or rf is None:
                logger.info("ML Models not found. Training default baseline models...")
                X, y = self.trainer.prepare_dataset(None)
                iso = self.trainer.train_isolation_forest(X)
                rf, _ = self.trainer.train_random_forest(X, y)
            return iso, rf
        except Exception as e:
            logger.error(f"Error loading/training default models: {e}")
            return None, None

    def detect(self, onu_data: Dict[str, Any]) -> AnomalyResult:
        """Calculates anomaly scores for a given ONU data log entry."""
        onu_id = onu_data.get("onu_id", onu_data.get("serial_number", "UNKNOWN"))
        features = self.extractor.extract_features(onu_data).reshape(1, -1)

        # Fallback if models are missing
        if self.iso_model is None:
            return AnomalyResult(onu_id, 0.0, "NORMAL", [], "No action required (model missing).")

        # Unsupervised prediction (-1 for outlier, 1 for inlier)
        iso_pred = self.iso_model.predict(features)[0]
        # Get decision function score (offset so that higher is more anomalous)
        raw_score = self.iso_model.decision_function(features)[0]
        # Normalize score between 0.0 and 1.0
        normalized_score = float(1.0 / (1.0 + np.exp(raw_score * 10)))

        # Supervised prediction (if available)
        rf_label = 1
        if self.rf_model is not None:
            rf_label = self.rf_model.predict(features)[0]

        reasons = []
        # Check rule violations for human explanation
        optical_power = float(onu_data.get("optical_power", -20.0))
        if optical_power < -27.0 or optical_power > -10.0:
            reasons.append(f"Abnormal optical power level: {optical_power} dBm")
        
        omci_freq = float(onu_data.get("omci_freq", 30.0))
        if omci_freq > 100.0:
            reasons.append(f"High frequency of OMCI messages: {omci_freq}/min")

        if not onu_data.get("port_consistent", True):
            reasons.append("ONU switched OLT ports unexpectedly")

        rereg_freq = int(onu_data.get("rereg_freq", 0))
        if rereg_freq > 5:
            reasons.append(f"High registration flap frequency: {rereg_freq}/hr")

        # Compile final label
        if rf_label == -1 or iso_pred == -1:
            if normalized_score > 0.75:
                label = "FAKE"
                action = "BLOCK ONU connection at OLT port immediately. Flag hardware serial."
            else:
                label = "SUSPICIOUS"
                action = "Isolate ONU to quarantine VLAN. Initiate deep traffic inspection."
        else:
            label = "NORMAL"
            action = "Keep connection authorized."

        return AnomalyResult(onu_id, normalized_score, label, reasons, action)
        
import numpy as np
