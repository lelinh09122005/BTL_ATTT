from typing import Dict, List, Any
from loguru import logger

class CVEAnalyzer:
    def __init__(self):
        # Local CVE Database Mapping
        self.cve_db: Dict[str, Dict[str, Any]] = {
            "CVE-2025-29525": {
                "id": "CVE-2025-29525",
                "description": "GPON Authentication Bypass via spoofed registration packets without valid LOID.",
                "severity": "CRITICAL",
                "module": "gpon",
                "category": "auth",
                "remediation": "Update OLT firmware and enforce double verification using both SN and PLOAM password. Restrict registration to whitelisted LOIDs."
            },
            "CVE-2025-63353": {
                "id": "CVE-2025-63353",
                "description": "ONU Impersonation through Serial Number spoofing/cloning.",
                "severity": "CRITICAL",
                "module": "gpon",
                "category": "auth",
                "remediation": "Enable AES-128 downstream encryption and enforce PLOAM password authorization on OLT."
            },
            "CVE-2026-2907": {
                "id": "CVE-2026-2907",
                "description": "Command Injection in GPON ONU Web administrative interface.",
                "severity": "CRITICAL",
                "module": "gpon",
                "category": "access_control",
                "remediation": "Update ONU firmware and add strict character filtering (;, |, $, &) on all user input inputs."
            },
            "CVE-2026-5339": {
                "id": "CVE-2026-5339",
                "description": "Command Injection in GPON ONU CGI diagnostic script.",
                "severity": "CRITICAL",
                "module": "gpon",
                "category": "access_control",
                "remediation": "Disable CGI administrative access on WAN interfaces. Apply the vendor patch."
            },
            "CVE-2025-10957": {
                "id": "CVE-2025-10957",
                "description": "Unrestricted FTP access on GPON ONU exposing system configuration files.",
                "severity": "HIGH",
                "module": "gpon",
                "category": "access_control",
                "remediation": "Disable FTP service or change default credentials. Set strict ACL rules to prevent access from WAN."
            }
        }

    def load_cve_database(self) -> Dict[str, Dict[str, Any]]:
        logger.info("Loaded local CVE Database containing GPON security definitions.")
        return self.cve_db

    def get_cve_info(self, cve_id: str) -> Dict[str, Any]:
        """Retrieves details of a specific CVE."""
        return self.cve_db.get(cve_id, {"error": f"CVE {cve_id} not found in database."})

    def map_to_test_module(self, cve_id: str) -> str:
        """Returns the module path corresponding to the given CVE."""
        cve = self.cve_db.get(cve_id)
        if cve:
            return f"{cve['module']}/{cve['category']}"
        return "unknown"

    def get_remediation(self, cve_id: str) -> str:
        """Helper to get remediation recommendation for a CVE."""
        cve = self.cve_db.get(cve_id)
        return cve["remediation"] if cve else "No recommendation available."
