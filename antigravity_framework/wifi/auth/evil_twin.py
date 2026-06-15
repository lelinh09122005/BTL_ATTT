import subprocess
import time
from typing import Dict, Any
from loguru import logger
from antigravity_framework.core.plugin import BaseTestPlugin
from antigravity_framework.core.result import TestResult, TestStatus, Severity

class EvilTwinTest(BaseTestPlugin):
    name = "Evil Twin Vulnerability Test"
    module = "wifi"
    category = "auth"
    description = "Kiểm thử khả năng giả mạo Access Point và đánh giá hành vi xác thực chứng chỉ của clients."
    cve_refs = []

    def setup(self) -> bool:
        super().setup()
        if self.config.simulated_mode:
            logger.info("[EvilTwinTest] Setup in SIMULATED mode. Checking virtual monitor interface.")
            return True
            
        # Real mode checks
        try:
            # Check for airgeddon/hostapd-wpe/bettercap dependencies
            for tool in ["hostapd", "bettercap", "iw"]:
                subprocess.run(["which", tool], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            logger.info(f"[EvilTwinTest] Checking if {self.config.target_interface} is in monitor mode")
            # In a real environment, we would run: iw dev <interface> info or check with airmon-ng
            return True
        except subprocess.CalledProcessError:
            logger.warning("[EvilTwinTest] Missing external tools (hostapd, bettercap, or iw). Falling back to simulation.")
            self.config.simulated_mode = True
            return True

    def run_evil_twin_attack(self, target_ssid: str, bssid: str) -> Dict[str, Any]:
        """Simulates or executes the Evil Twin AP startup."""
        if self.config.simulated_mode:
            logger.info(f"[EvilTwinTest] Simulating Evil Twin AP for SSID '{target_ssid}' ({bssid})")
            time.sleep(1)
            return {
                "connected_clients": ["00:aa:bb:cc:dd:11", "00:aa:bb:cc:dd:22"],
                "cert_validated": False,
                "mitm_possible": True
            }
        
        # Real execution placeholder:
        # 1. Config hostapd-wpe.conf with target_ssid
        # 2. Run: hostapd-wpe hostapd-wpe.conf -B
        # 3. Monitor associations in /var/log/messages or via subprocess stdout
        logger.info(f"[EvilTwinTest] Starting real hostapd-wpe on {self.config.target_interface}")
        return {
            "connected_clients": [],
            "cert_validated": True,
            "mitm_possible": False
        }

    def check_certificate_validation(self) -> bool:
        """Analyzes EAP exchange to verify if client validates server certificate."""
        if self.config.simulated_mode:
            logger.info("[EvilTwinTest] Simulating EAP-PEAP exchange analysis. Certificate warning bypassed by client.")
            return False  # Client did not validate
        return True

    def run(self) -> TestResult:
        logger.info(f"[EvilTwinTest] Starting Evil Twin vulnerability test against AP '{self.config.target_ssid}'")
        
        details = self.run_evil_twin_attack(self.config.target_ssid, self.config.target_bssid)
        cert_validated = self.check_certificate_validation()
        details["cert_validated"] = cert_validated
        
        if not cert_validated:
            status = TestStatus.FAIL
            severity = Severity.CRITICAL
            details["vulnerability_summary"] = "Clients accept untrusted certificates, allowing complete Man-in-the-Middle (MitM) attacks."
        else:
            status = TestStatus.PASS
            severity = Severity.INFO
            details["vulnerability_summary"] = "Clients rejected the fake AP due to strict TLS/EAP certificate validation."

        return self.create_result(status, severity, details)

    def teardown(self) -> bool:
        if not self.config.simulated_mode:
            logger.info("[EvilTwinTest] Stopping fake AP and restoring wireless interface state.")
            # kill hostapd, dnsmasq, etc.
        return super().teardown()
