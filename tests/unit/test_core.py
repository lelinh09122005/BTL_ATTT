import pytest
from datetime import datetime
from antigravity_framework.core.config import Config
from antigravity_framework.core.result import TestResult, TestStatus, Severity
from antigravity_framework.core.events import EventBus
from antigravity_framework.core.plugin import BaseTestPlugin
from antigravity_framework.core.engine import AntiGravityEngine

class DummyTestPlugin(BaseTestPlugin):
    name = "Dummy Test Case"
    module = "wifi"
    category = "auth"
    
    def run(self) -> TestResult:
        return self.create_result(
            status=TestStatus.PASS,
            severity=Severity.INFO,
            details={"dummy": True}
        )

def test_config_load_defaults():
    config = Config()
    assert config.simulated_mode is True
    assert config.target_interface == "wlan0mon"
    assert config.test_timeout == 30

def test_test_result_to_dict():
    res = TestResult(
        test_id="DummyTest",
        name="Dummy",
        module="wifi",
        category="auth",
        status=TestStatus.PASS,
        severity=Severity.INFO,
        duration_ms=100
    )
    d = res.to_dict()
    assert d["status"] == "PASS"
    assert d["severity"] == "INFO"
    assert "timestamp" in d
    assert d["duration_ms"] == 100

def test_event_bus():
    bus = EventBus()
    triggered = []
    
    def callback(data):
        triggered.append(data)
        
    bus.subscribe("test_event", callback)
    bus.publish("test_event", "hello")
    
    assert len(triggered) == 1
    assert triggered[0] == "hello"

def test_engine_run_plugin():
    config = Config()
    engine = AntiGravityEngine(config)
    plugin = DummyTestPlugin(config)
    
    engine.register_plugin("dummy", plugin)
    assert "dummy" in engine.plugins
    
    result = engine.run_plugin("dummy")
    assert result.status == TestStatus.PASS
    assert result.duration_ms >= 0
    assert len(engine.results) == 1
