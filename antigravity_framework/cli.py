import os
import typer
import uvicorn
from typing import Optional
from loguru import logger

from antigravity_framework.core.config import Config
from antigravity_framework.core.engine import AntiGravityEngine
from antigravity_framework.reporting.report_builder import ReportBuilder
from antigravity_framework.reporting.dashboard import DashboardServer

app = typer.Typer(help="AntiGravity - WiFi & GPON Security Testing Framework CLI")

def initialize_engine(config_file: Optional[str]) -> AntiGravityEngine:
    config = Config(config_file)
    engine = AntiGravityEngine(config)
    
    # Import and register plugins
    from antigravity_framework.wifi.auth.evil_twin import EvilTwinTest
    from antigravity_framework.wifi.auth.dot1x import Dot1XTest
    from antigravity_framework.wifi.access_control.acl_test import ACLTest
    from antigravity_framework.wifi.access_control.mac_filter import MACFilterTest
    from antigravity_framework.wifi.access_control.client_isolation import ClientIsolationTest
    from antigravity_framework.wifi.encryption.krack import KRACKTest
    from antigravity_framework.wifi.encryption.kr00k import Kr00kTest
    from antigravity_framework.wifi.encryption.fragattacks import FragAttacksTest
    from antigravity_framework.wifi.encryption.wpa3_fuzzing import WPA3FuzzingTest

    from antigravity_framework.gpon.auth.loid_test import LOIDTest
    from antigravity_framework.gpon.auth.serial_number import SerialNumberTest
    from antigravity_framework.gpon.auth.onu_registration import ONURegistrationTest
    from antigravity_framework.gpon.encryption.key_exchange import GPONKeyExchangeTest
    from antigravity_framework.gpon.encryption.aes128_test import AES128Test
    from antigravity_framework.gpon.encryption.optical_tap import OpticalTapTest
    from antigravity_framework.gpon.access_control.cmd_injection import CommandInjectionTest
    from antigravity_framework.gpon.access_control.ftp_access import FTPAccessTest
    from antigravity_framework.gpon.access_control.web_api_test import WebAPITest

    from antigravity_framework.cve.cve_2025_29525 import CVE202529525Test

    # WiFi Plugins
    engine.register_plugin("evil_twin", EvilTwinTest(config))
    engine.register_plugin("dot1x", Dot1XTest(config))
    engine.register_plugin("wifi_acl", ACLTest(config))
    engine.register_plugin("mac_filter", MACFilterTest(config))
    engine.register_plugin("client_isolation", ClientIsolationTest(config))
    engine.register_plugin("krack", KRACKTest(config))
    engine.register_plugin("kr00k", Kr00kTest(config))
    engine.register_plugin("fragattacks", FragAttacksTest(config))
    engine.register_plugin("wpa3_fuzzing", WPA3FuzzingTest(config))

    # GPON Plugins
    engine.register_plugin("loid_test", LOIDTest(config))
    engine.register_plugin("serial_number", SerialNumberTest(config))
    engine.register_plugin("onu_registration", ONURegistrationTest(config))
    engine.register_plugin("key_exchange", GPONKeyExchangeTest(config))
    engine.register_plugin("aes128_test", AES128Test(config))
    engine.register_plugin("optical_tap", OpticalTapTest(config))
    engine.register_plugin("cmd_injection", CommandInjectionTest(config))
    engine.register_plugin("ftp_access", FTPAccessTest(config))
    engine.register_plugin("web_api", WebAPITest(config))

    # CVE Plugins
    engine.register_plugin("cve_2025_29525", CVE202529525Test(config))
    
    return engine

@app.command()
def scan(
    module: Optional[str] = typer.Option(None, "--module", "-m", help="Run specific module: 'wifi' or 'gpon'"),
    config_file: Optional[str] = typer.Option(None, "--config", "-c", help="Path to config YAML file"),
    simulated: bool = typer.Option(True, "--simulated/--real", help="Run tests in simulated or real mode")
):
    """Executes security testing plugins and exports reports."""
    engine = initialize_engine(config_file)
    engine.config.simulated_mode = simulated
    
    typer.echo(f"Starting AntiGravity scan. Simulated mode: {simulated}")
    
    if module:
        results = engine.run_module(module)
    else:
        results = engine.run_all()
        
    typer.echo("\n--- TEST RESULTS ---")
    for r in results:
        status_color = typer.colors.GREEN if r.status.value == "PASS" else typer.colors.RED
        if r.status.value == "ERROR" or r.status.value == "SKIP":
            status_color = typer.colors.YELLOW
        typer.secho(f"[{r.module.upper()}] {r.name}: {r.status.value} ({r.severity.value})", fg=status_color)
        
    # Build reports
    builder = ReportBuilder(engine.config.output_dir)
    builder.build_json_report(results)
    builder.build_html_report(results)
    
    typer.secho(f"\nScan completed. Reports generated in {engine.config.output_dir}/", fg=typer.colors.CYAN)

@app.command()
def serve(
    host: str = typer.Option("127.0.0.1", "--host", "-h", help="Host address to bind to"),
    port: int = typer.Option(8000, "--port", "-p", help="Port to bind to"),
    config_file: Optional[str] = typer.Option(None, "--config", "-c", help="Path to config YAML file")
):
    """Starts the REST API backend server (FastAPI)."""
    typer.echo(f"Starting AntiGravity REST API at http://{host}:{port}")
    # Run uvicorn server pointing to main FastAPI app
    uvicorn.run("antigravity_framework.api.main:app", host=host, port=port, reload=True)

@app.command()
def dashboard(
    host: str = typer.Option("127.0.0.1", "--host", "-h", help="Host address to bind to"),
    port: int = typer.Option(8080, "--port", "-p", help="Port to bind to"),
    report_dir: str = typer.Option("./reports", "--report-dir", help="Directory where reports are saved")
):
    """Runs a web server to view the generated HTML security reports."""
    server = DashboardServer(report_dir)
    server.start(host=host, port=port)

if __name__ == "__main__":
    app()
