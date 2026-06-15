import os
from typing import Dict, Any, List
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse, HTMLResponse
from pydantic import BaseModel
from loguru import logger

from antigravity_framework.core.config import Config
from antigravity_framework.core.engine import AntiGravityEngine
from antigravity_framework.core.result import TestResult
from antigravity_framework.reporting.report_builder import ReportBuilder
from antigravity_framework.ml.onu_detector import AIONUDetector

# Setup global configurations
config = Config()
engine = AntiGravityEngine(config)
report_builder = ReportBuilder(config.output_dir)
onu_detector = AIONUDetector()

# Register all plugins
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

app = FastAPI(title="AntiGravity API", description="REST API for WiFi & GPON Security Testing Framework")

class ScanRequest(BaseModel):
    simulated_mode: bool = True
    target_ssid: str = "Test_WiFi"
    gpon_olt_ip: str = "192.168.100.1"

class ONULogEntry(BaseModel):
    serial_number: str
    loid: str = ""
    optical_power: float = -20.0
    omci_freq: float = 30.0
    traffic_deviation: float = 0.0
    port_consistent: bool = True
    rereg_freq: int = 0

def run_async_scan(module: str = None):
    """Orchestrates tests and updates generated static report content."""
    if module:
        engine.run_module(module)
    else:
        engine.run_all()
    report_builder.build_json_report(engine.results)
    report_builder.build_html_report(engine.results)

@app.post("/api/v1/scan/wifi")
async def start_wifi_scan(request: ScanRequest, background_tasks: BackgroundTasks):
    config.simulated_mode = request.simulated_mode
    config.target_ssid = request.target_ssid
    background_tasks.add_task(run_async_scan, "wifi")
    return {"status": "started", "message": "WiFi scanning suite initiated in background."}

@app.post("/api/v1/scan/gpon")
async def start_gpon_scan(request: ScanRequest, background_tasks: BackgroundTasks):
    config.simulated_mode = request.simulated_mode
    config.gpon_olt_ip = request.gpon_olt_ip
    background_tasks.add_task(run_async_scan, "gpon")
    return {"status": "started", "message": "GPON scanning suite initiated in background."}

@app.post("/api/v1/scan/all")
async def start_all_scan(request: ScanRequest, background_tasks: BackgroundTasks):
    config.simulated_mode = request.simulated_mode
    config.target_ssid = request.target_ssid
    config.gpon_olt_ip = request.gpon_olt_ip
    background_tasks.add_task(run_async_scan)
    return {"status": "started", "message": "Full WiFi & GPON scanning suite initiated in background."}

@app.get("/api/v1/results")
async def get_results():
    return [r.to_dict() for r in engine.results]

@app.get("/api/v1/results/{test_id}")
async def get_result_by_id(test_id: str):
    for r in engine.results:
        if r.test_id == test_id:
            return r.to_dict()
    raise HTTPException(status_code=404, detail="Test result not found.")

@app.get("/api/v1/report/{format}")
async def get_report(format: str):
    if format == "json":
        path = os.path.join(config.output_dir, "report.json")
    elif format == "html":
        path = os.path.join(config.output_dir, "report.html")
    elif format == "pdf":
        path = os.path.join(config.output_dir, "report.pdf")
    else:
        raise HTTPException(status_code=400, detail="Invalid report format. Use json, html or pdf.")
        
    if os.path.exists(path):
        return FileResponse(path)
    raise HTTPException(status_code=404, detail=f"Report file in {format} format has not been generated yet.")

@app.post("/api/v1/ml/onu-status")
async def check_onu_anomaly(log_entry: ONULogEntry):
    res = onu_detector.analyze_onu(log_entry.model_dump())
    return res.to_dict()

@app.post("/api/v1/ml/train")
async def retrain_model(custom_logs: List[ONULogEntry]):
    logs_dict = [log.model_dump() for log in custom_logs]
    metrics = onu_detector.train_new_model(logs_dict)
    return {"status": "success", "evaluation_metrics": metrics}
