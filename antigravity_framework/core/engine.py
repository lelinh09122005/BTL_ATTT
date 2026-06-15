from typing import Dict, List, Any
from loguru import logger
from antigravity_framework.core.config import Config
from antigravity_framework.core.events import event_bus, EventBus
from antigravity_framework.core.result import TestResult, TestStatus, Severity
from antigravity_framework.core.plugin import BaseTestPlugin

class AntiGravityEngine:
    def __init__(self, config: Config = None):
        self.config = config or Config()
        self.event_bus = event_bus
        self.plugins: Dict[str, BaseTestPlugin] = {}
        self.results: List[TestResult] = []

    def register_plugin(self, name: str, plugin: BaseTestPlugin):
        """Registers a test plugin with the engine."""
        self.plugins[name] = plugin
        logger.info(f"Registered plugin: {name} ({plugin.module}/{plugin.category})")

    def run_plugin(self, name: str) -> TestResult:
        """Executes a single plugin by name, handling its lifecycle."""
        plugin = self.plugins.get(name)
        if not plugin:
            raise ValueError(f"Plugin {name} not found.")

        logger.info(f"Starting test execution: {name}")
        self.event_bus.publish("test_start", {"name": name})
        
        try:
            setup_success = plugin.setup()
            if not setup_success:
                logger.error(f"Setup failed for plugin: {name}")
                result = plugin.create_result(
                    status=TestStatus.ERROR,
                    severity=Severity.HIGH,
                    details={"error": "Setup phase failed."}
                )
            else:
                result = plugin.run()
        except Exception as e:
            logger.exception(f"Unhandled exception during plugin execution: {name}")
            result = TestResult(
                test_id=plugin.__class__.__name__,
                name=plugin.name,
                module=plugin.module,
                category=plugin.category,
                status=TestStatus.ERROR,
                severity=Severity.HIGH,
                details={"error": str(e), "exception_type": type(e).__name__},
                cve_refs=plugin.cve_refs.copy()
            )
        finally:
            plugin.teardown()
            result.duration_ms = plugin.duration_ms
        
        logger.info(f"Completed test execution: {name}. Status: {result.status.value}")
        self.event_bus.publish("test_complete", result.to_dict())
        
        # Keep track of the result
        # Remove previous result of the same plugin if exists
        self.results = [r for r in self.results if r.test_id != result.test_id]
        self.results.append(result)
        
        return result

    def run_all(self) -> List[TestResult]:
        """Runs all registered plugins."""
        logger.info("Executing all registered plugins...")
        self.event_bus.publish("suite_start", {"total": len(self.plugins)})
        for name in list(self.plugins.keys()):
            self.run_plugin(name)
        self.event_bus.publish("suite_complete", {"results_count": len(self.results)})
        return self.results

    def run_module(self, module_name: str) -> List[TestResult]:
        """Runs all plugins belonging to a specific module (e.g. 'wifi', 'gpon')."""
        logger.info(f"Executing plugins in module: {module_name}...")
        matching_plugins = [name for name, p in self.plugins.items() if p.module == module_name]
        self.event_bus.publish("suite_start", {"total": len(matching_plugins)})
        for name in matching_plugins:
            self.run_plugin(name)
        self.event_bus.publish("suite_complete", {"results_count": len(self.results)})
        return [r for r in self.results if r.module == module_name]

    def clear_results(self):
        """Clears stored test results."""
        self.results.clear()
