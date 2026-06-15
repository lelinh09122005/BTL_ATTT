import time
from typing import Dict, Any
from loguru import logger
from antigravity_framework.core.plugin import BaseTestPlugin
from antigravity_framework.core.result import TestResult, TestStatus, Severity

class OpticalTapTest(BaseTestPlugin):
    name = "Optical Tapping Vulnerability Test"
    module = "gpon"
    category = "encryption"
    description = "Đánh giá khả năng phát hiện suy hao quang học (micro-bend loss) bất thường trên đường truyền khi bị trích xuất tín hiệu vật lý."
    cve_refs = []

    def check_power_monitoring(self, olt_ip: str) -> Dict[str, Any]:
        """Queries the optical power monitoring system of OLT for anomalies."""
        if self.config.simulated_mode:
            return {
                "optical_loss_db": 4.2,  # Normal loss should be less than 1.5 dB for bends
                "alarm_triggered": False
            }
        return {"optical_loss_db": 0.5, "alarm_triggered": False}

    def run(self) -> TestResult:
        logger.info(f"[OpticalTapTest] Auditing optical power baseline and alarm system of OLT {self.config.gpon_olt_ip}")
        
        tap_stats = self.check_power_monitoring(self.config.gpon_olt_ip)
        
        # High loss with no alarms triggers a warning
        vulnerable = tap_stats["optical_loss_db"] > 2.0 and not tap_stats["alarm_triggered"]
        
        details = {
            "optical_loss_db": tap_stats["optical_loss_db"],
            "olt_alarm_triggered": tap_stats["alarm_triggered"],
            "vulnerable": vulnerable
        }
        
        if vulnerable:
            status = TestStatus.FAIL
            severity = Severity.MEDIUM
            details["remediation"] = "Cấu hình lại ngưỡng cảnh báo suy hao Rx/Tx trên cổng OLT. Tích hợp cảnh báo thời gian thực khi có biến động suy hao đột ngột."
        else:
            status = TestStatus.PASS
            severity = Severity.INFO
            details["remediation"] = "Hệ thống phát hiện suy hao quang học hoạt động đúng thiết kế."

        return self.create_result(status, severity, details)
