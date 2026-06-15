from typing import Dict, Any, List
from loguru import logger
from antigravity_framework.ml.anomaly_detector import ONUAnomalyDetector, AnomalyResult
from antigravity_framework.ml.model_trainer import ONUModelTrainer

class AIONUDetector:
    def __init__(self, model_dir: str = "./models"):
        self.detector = ONUAnomalyDetector(model_dir)
        self.trainer = ONUModelTrainer(model_dir)

    def analyze_onu(self, onu_record: Dict[str, Any]) -> AnomalyResult:
        """Analyzes a single ONU record and returns an AnomalyResult."""
        logger.info(f"ML Layer: Checking ONU {onu_record.get('serial_number')} profile")
        return self.detector.detect(onu_record)

    def train_new_model(self, custom_logs: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Triggers model training using custom logged interactions."""
        logger.info("ML Layer: Request to train models with new input records")
        X, y = self.trainer.prepare_dataset(custom_logs)
        self.trainer.train_isolation_forest(X)
        _, metrics = self.trainer.train_random_forest(X, y)
        
        # Reload models in detector
        self.detector.iso_model, self.detector.rf_model = self.trainer.load_models()
        return metrics
