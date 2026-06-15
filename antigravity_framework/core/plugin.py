import time
from abc import ABC, abstractmethod
from typing import List, Dict, Any
from datetime import datetime
from loguru import logger
from antigravity_framework.core.config import Config
from antigravity_framework.core.result import TestResult, TestStatus, Severity

class BaseTestPlugin(ABC):
    """Abstract base class for all WiFi and GPON test plugins."""
    
    name: str = "Base Test Plugin"
    module: str = "core"            # 'wifi' | 'gpon' | 'cve'
    category: str = "general"       # 'auth' | 'encryption' | 'access_control'
    description: str = ""
    cve_refs: List[str] = []

    def __init__(self, config: Config):
        self.config = config
        self.duration_ms = 0
        self.start_time = 0.0

    def setup(self) -> bool:
        """Preparatory steps before executing the test. Returns True if successful."""
        logger.info(f"[{self.name}] Running setup...")
        self.start_time = time.time()
        return True

    @abstractmethod
    def run(self) -> TestResult:
        """Executes the test and returns the TestResult object."""
        pass

    def teardown(self) -> bool:
        """Cleanup steps after executing the test. Returns True if successful."""
        logger.info(f"[{self.name}] Running teardown...")
        if self.start_time > 0:
            self.duration_ms = int((time.time() - self.start_time) * 1000)
        return True

    def create_result(self, status: TestStatus, severity: Severity, details: Dict[str, Any]) -> TestResult:
        """Convenience method to construct a TestResult object for this plugin."""
        return TestResult(
            test_id=self.__class__.__name__,
            name=self.name,
            module=self.module,
            category=self.category,
            status=status,
            severity=severity,
            details=details,
            cve_refs=self.cve_refs.copy(),
            timestamp=datetime.now(),
            duration_ms=self.duration_ms
        )
