import os
import yaml
from typing import Dict, Any, List

class Config:
    def __init__(self, config_path: str = None):
        self.target_interface: str = "wlan0mon"
        self.target_ssid: str = "Test_WiFi"
        self.target_bssid: str = "00:11:22:33:44:55"
        self.gpon_olt_ip: str = "192.168.100.1"
        self.gpon_interface: str = "eth1"
        self.onu_list: List[str] = ["GPON00000001", "GPON00000002"]
        self.onu_mgmt_ip: str = "192.168.100.10"
        self.test_timeout: int = 30
        self.output_dir: str = "./reports"
        self.log_level: str = "INFO"
        self.simulated_mode: bool = True  # Default to simulation mode if hardware is missing
        
        if config_path:
            self.load_from_yaml(config_path)

    def load_from_yaml(self, path: str):
        """Loads configuration from a YAML file, merging with default values."""
        if not os.path.exists(path):
            return
        
        try:
            with open(path, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
                if data:
                    self.target_interface = data.get("target_interface", self.target_interface)
                    self.target_ssid = data.get("target_ssid", self.target_ssid)
                    self.target_bssid = data.get("target_bssid", self.target_bssid)
                    self.gpon_olt_ip = data.get("gpon_olt_ip", self.gpon_olt_ip)
                    self.gpon_interface = data.get("gpon_interface", self.gpon_interface)
                    self.onu_list = data.get("onu_list", self.onu_list)
                    self.onu_mgmt_ip = data.get("onu_mgmt_ip", self.onu_mgmt_ip)
                    self.test_timeout = data.get("test_timeout", self.test_timeout)
                    self.output_dir = data.get("output_dir", self.output_dir)
                    self.log_level = data.get("log_level", self.log_level)
                    self.simulated_mode = data.get("simulated_mode", self.simulated_mode)
        except Exception as e:
            # Fall back to default if file reading fails
            pass

    def to_dict(self) -> Dict[str, Any]:
        return {
            "target_interface": self.target_interface,
            "target_ssid": self.target_ssid,
            "target_bssid": self.target_bssid,
            "gpon_olt_ip": self.gpon_olt_ip,
            "gpon_interface": self.gpon_interface,
            "onu_list": self.onu_list,
            "onu_mgmt_ip": self.onu_mgmt_ip,
            "test_timeout": self.test_timeout,
            "output_dir": self.output_dir,
            "log_level": self.log_level,
            "simulated_mode": self.simulated_mode,
        }
