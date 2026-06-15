from enum import Enum
from dataclasses import dataclass, field, asdict
from datetime import datetime
from typing import Dict, List, Any

class TestStatus(str, Enum):
    PASS = "PASS"
    FAIL = "FAIL"
    ERROR = "ERROR"
    SKIP = "SKIP"

class Severity(str, Enum):
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"
    INFO = "INFO"

@dataclass
class TestResult:
    test_id: str
    name: str
    module: str               # 'wifi' | 'gpon'
    category: str             # 'auth' | 'encryption' | 'access_control'
    status: TestStatus
    severity: Severity
    details: Dict[str, Any] = field(default_factory=dict)
    cve_refs: List[str] = field(default_factory=list)
    timestamp: datetime = field(default_factory=datetime.now)
    duration_ms: int = 0

    def to_dict(self) -> Dict[str, Any]:
        """Converts the dataclass instance to a dictionary, serializing datetime and Enums."""
        data = asdict(self)
        data['status'] = self.status.value
        data['severity'] = self.severity.value
        data['timestamp'] = self.timestamp.isoformat()
        return data
