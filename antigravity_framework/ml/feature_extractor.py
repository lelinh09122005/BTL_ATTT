import numpy as np
import pandas as pd
from typing import Dict, Any, List
from loguru import logger

class ONUFeatureExtractor:
    def __init__(self):
        # Define features order
        self.feature_names = [
            "registration_time_pattern",     # Hour of day (0-23)
            "optical_power_level",           # dBm (negative values, e.g. -22.5)
            "omci_message_frequency",        # Messages per minute
            "serial_number_vendor_prefix",   # Int mapped vendor prefix
            "loid_format_validity",          # 1 if valid, 0 if invalid
            "traffic_volume_baseline",       # deviation score
            "location_consistency",          # 1 if same port, 0 if changed
            "registration_frequency"         # Re-regs per hour
        ]

    def map_vendor_prefix(self, sn: str) -> int:
        """Simple mapping of common GPON vendors to integers."""
        prefix = sn[:4].upper()
        mapping = {
            "HWTC": 1,  # Huawei
            "ZTEG": 2,  # ZTE
            "ALCL": 3,  # Alcatel
            "ELTX": 4,  # Eltex
            "VNPT": 5,  # VNPT
        }
        return mapping.get(prefix, 99)  # 99 for unknown vendors

    def extract_features(self, onu_data: Dict[str, Any]) -> np.ndarray:
        """Extracts a feature vector from raw ONU registry information."""
        try:
            # Registration hour
            reg_hour = onu_data.get("registration_hour", 12)
            
            # Optical power (expected between -28.0 and -8.0 dBm)
            optical_power = float(onu_data.get("optical_power", -20.0))
            
            # OMCI Frequency (messages/min)
            omci_freq = float(onu_data.get("omci_freq", 30.0))
            
            # Vendor prefix mapping
            vendor_id = self.map_vendor_prefix(onu_data.get("serial_number", "HWTC00000000"))
            
            # LOID valid format
            loid = onu_data.get("loid", "")
            loid_valid = 1 if len(loid) > 4 and "_" in loid else 0
            
            # Traffic baseline deviation (e.g. standard deviation distance)
            traffic_dev = float(onu_data.get("traffic_deviation", 0.0))
            
            # Port changes
            port_consistent = 1 if onu_data.get("port_consistent", True) else 0
            
            # Re-registration frequency (number of re-registrations in last hour)
            rereg_freq = int(onu_data.get("rereg_freq", 0))
            
            feature_vector = np.array([
                reg_hour,
                optical_power,
                omci_freq,
                vendor_id,
                loid_valid,
                traffic_dev,
                port_consistent,
                rereg_freq
            ])
            return feature_vector
            
        except Exception as e:
            logger.error(f"Error extracting features: {e}")
            # Return a default vector on failure
            return np.array([12, -20.0, 30.0, 1, 1, 0.0, 1, 0])

    def create_batch_dataset(self, log_records: List[Dict[str, Any]]) -> pd.DataFrame:
        """Builds a Pandas DataFrame from raw ONU log dictionaries."""
        features_list = []
        for record in log_records:
            vector = self.extract_features(record)
            features_list.append(vector)
            
        df = pd.DataFrame(features_list, columns=self.feature_names)
        return df
