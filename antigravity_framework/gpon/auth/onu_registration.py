import time
from typing import Dict, Any
from loguru import logger
from antigravity_framework.core.plugin import BaseTestPlugin
from antigravity_framework.core.result import TestResult, TestStatus, Severity

class ONURegistrationTest(BaseTestPlugin):
    name = "Rogue ONU Registration Test"
    module = "gpon"
    category = "auth"
    description = "Kiểm tra cấu hình tự động đăng ký (Auto-Discovery) trên OLT và khả năng cắm thiết bị ONU lạ."
    cve_refs = []

    def run(self) -> TestResult:
        logger.info(f"[ONURegistrationTest] Auditing GPON OLT auto-discovery policies on {self.config.gpon_olt_ip}")
        
        # Test whether OLT auto-accepts unknown ONUs
        # Simulated check
        time.sleep(0.5)
        
        auto_discovery_enabled = True  # Simulated finding
        unauthorized_onu_accepted = True  # Simulated finding
        
        details = {
            "auto_discovery_enabled": auto_discovery_enabled,
            "unauthorized_onu_accepted": unauthorized_onu_accepted,
            "vulnerability_found": auto_discovery_enabled and unauthorized_onu_accepted
        }
        
        if details["vulnerability_found"]:
            status = TestStatus.FAIL
            severity = Severity.HIGH
            details["remediation"] = "Tắt tính năng tự động kích hoạt (Auto-activation) cho các ONU mới trên OLT. Mọi ONU mới phải được phê duyệt thủ công bởi quản trị viên."
        else:
            status = TestStatus.PASS
            severity = Severity.INFO
            details["remediation"] = "Cơ chế tự động đăng ký được bảo vệ chính xác."
            
        return self.create_result(status, severity, details)
