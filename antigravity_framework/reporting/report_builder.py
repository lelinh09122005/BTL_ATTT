import os
import json
from datetime import datetime
from typing import List, Dict, Any
from jinja2 import Template
from loguru import logger
from antigravity_framework.core.result import TestResult

class ReportBuilder:
    def __init__(self, output_dir: str = "./reports"):
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)

    def build_json_report(self, results: List[TestResult]) -> str:
        """Generates a structured JSON string containing all test results and metadata."""
        report_data = {
            "title": "AntiGravity Security Audit Report",
            "timestamp": datetime.now().isoformat(),
            "summary": {
                "total_tests": len(results),
                "passed": sum(1 for r in results if r.status.value == "PASS"),
                "failed": sum(1 for r in results if r.status.value == "FAIL"),
                "errors": sum(1 for r in results if r.status.value == "ERROR"),
                "skipped": sum(1 for r in results if r.status.value == "SKIP"),
            },
            "results": [r.to_dict() for r in results]
        }
        
        output_path = os.path.join(self.output_dir, "report.json")
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(report_data, f, indent=4, ensure_ascii=False)
            
        logger.info(f"Saved JSON report to {output_path}")
        return json.dumps(report_data, indent=2, ensure_ascii=False)

    def build_html_report(self, results: List[TestResult]) -> str:
        """Generates a premium HTML report comparing WiFi/GPON features with Zero Trust assessments."""
        html_template = """
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>AntiGravity Security Audit Report</title>
            <style>
                :root {
                    --bg-dark: #0f172a;
                    --panel-dark: #1e293b;
                    --text-main: #f8fafc;
                    --text-muted: #94a3b8;
                    --accent-blue: #38bdf8;
                    --color-pass: #10b981;
                    --color-fail: #ef4444;
                    --color-warn: #f59e0b;
                }
                body {
                    background-color: var(--bg-dark);
                    color: var(--text-main);
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                    margin: 0;
                    padding: 20px;
                }
                .container {
                    max-width: 1100px;
                    margin: 0 auto;
                }
                header {
                    border-bottom: 2px solid var(--panel-dark);
                    padding-bottom: 20px;
                    margin-bottom: 30px;
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                }
                h1 { margin: 0; color: var(--accent-blue); font-size: 2.2rem; }
                .meta-time { color: var(--text-muted); font-size: 0.9rem; }
                .summary-cards {
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                    gap: 20px;
                    margin-bottom: 30px;
                }
                .card {
                    background-color: var(--panel-dark);
                    padding: 20px;
                    border-radius: 10px;
                    text-align: center;
                    border: 1px solid #334155;
                    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
                }
                .card-title { font-size: 0.9rem; color: var(--text-muted); text-transform: uppercase; }
                .card-value { font-size: 2.5rem; font-weight: bold; margin-top: 10px; }
                .pass { color: var(--color-pass); }
                .fail { color: var(--color-fail); }
                .warn { color: var(--color-warn); }
                
                table {
                    width: 100%;
                    border-collapse: collapse;
                    margin-bottom: 40px;
                    background-color: var(--panel-dark);
                    border-radius: 8px;
                    overflow: hidden;
                }
                th, td {
                    padding: 14px 20px;
                    text-align: left;
                    border-bottom: 1px solid #334155;
                }
                th {
                    background-color: #1e293b;
                    color: var(--accent-blue);
                    font-weight: 600;
                    text-transform: uppercase;
                    font-size: 0.85rem;
                }
                tr:last-child td { border-bottom: none; }
                .status-badge {
                    padding: 4px 10px;
                    border-radius: 20px;
                    font-size: 0.8rem;
                    font-weight: bold;
                    display: inline-block;
                }
                .badge-pass { background-color: rgba(16, 185, 129, 0.2); color: var(--color-pass); }
                .badge-fail { background-color: rgba(239, 68, 68, 0.2); color: var(--color-fail); }
                .badge-error { background-color: rgba(245, 158, 11, 0.2); color: var(--color-warn); }
                
                .comparison-table td { font-size: 0.95rem; }
                .remediation-box {
                    font-size: 0.85rem;
                    color: var(--text-muted);
                    background: #1e293b;
                    border-left: 4px solid var(--accent-blue);
                    padding: 8px 12px;
                    margin-top: 6px;
                    border-radius: 0 4px 4px 0;
                }
            </style>
        </head>
        <body>
            <div class="container">
                <header>
                    <div>
                        <h1>AntiGravity Security Report</h1>
                        <div class="meta-time">Generated on: {{ timestamp }}</div>
                    </div>
                </header>
                
                <div class="summary-cards">
                    <div class="card">
                        <div class="card-title">Total Tests</div>
                        <div class="card-value">{{ summary.total_tests }}</div>
                    </div>
                    <div class="card">
                        <div class="card-title">Passed</div>
                        <div class="card-value pass">{{ summary.passed }}</div>
                    </div>
                    <div class="card">
                        <div class="card-title">Failed</div>
                        <div class="card-value fail">{{ summary.failed }}</div>
                    </div>
                </div>

                <h2>1. WiFi vs GPON Security Comparison</h2>
                <table class="comparison-table">
                    <thead>
                        <tr>
                            <th>Security Dimension</th>
                            <th>WiFi (802.11) Status</th>
                            <th>GPON (G.984) Status</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr>
                            <td><strong>Authentication</strong></td>
                            <td>WPA3-SAE & 802.1X Enterprise</td>
                            <td>LOID & Serial Number</td>
                        </tr>
                        <tr>
                            <td><strong>Encryption</strong></td>
                            <td>AES-CCMP / GCMP (128/256-bit)</td>
                            <td>AES-128 downstream (Upstream unencrypted)</td>
                        </tr>
                        <tr>
                            <td><strong>Access Control</strong></td>
                            <td>MAC filtering & client isolation</td>
                            <td>OLT Port security & IP filters</td>
                        </tr>
                    </tbody>
                </table>

                <h2>2. Detailed Test Results</h2>
                <table>
                    <thead>
                        <tr>
                            <th>Module</th>
                            <th>Test Case</th>
                            <th>Severity</th>
                            <th>Status</th>
                        </tr>
                    </thead>
                    <tbody>
                        {% for test in results %}
                        <tr>
                            <td><strong>{{ test.module|upper }}</strong> ({{ test.category }})</td>
                            <td>
                                <div>{{ test.name }}</div>
                                <div style="font-size: 0.85rem; color: var(--text-muted); margin-top: 4px;">{{ test.details.vulnerability_summary or test.details.error or '' }}</div>
                                {% if test.status == 'FAIL' and test.details.remediation %}
                                <div class="remediation-box">
                                    <strong>Remediation:</strong> {{ test.details.remediation }}
                                </div>
                                {% endif %}
                            </td>
                            <td><span class="warn">{{ test.severity }}</span></td>
                            <td>
                                {% if test.status == 'PASS' %}
                                    <span class="status-badge badge-pass">PASS</span>
                                {% elif test.status == 'FAIL' %}
                                    <span class="status-badge badge-fail">FAIL</span>
                                {% else %}
                                    <span class="status-badge badge-error">ERROR</span>
                                {% endif %}
                            </td>
                        </tr>
                        {% endfor %}
                    </tbody>
                </table>
            </div>
        </body>
        </html>
        """
        
        # Build values
        summary = {
            "total_tests": len(results),
            "passed": sum(1 for r in results if r.status.value == "PASS"),
            "failed": sum(1 for r in results if r.status.value == "FAIL"),
            "errors": sum(1 for r in results if r.status.value == "ERROR")
        }
        
        template = Template(html_template)
        rendered_html = template.render(
            timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            summary=summary,
            results=[r.to_dict() for r in results]
        )
        
        output_path = os.path.join(self.output_dir, "report.html")
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(rendered_html)
            
        logger.info(f"Saved HTML report to {output_path}")
        return rendered_html
        
    def build_pdf_report(self, results: List[TestResult]) -> str:
        """Generates a PDF report using WeasyPrint or writes a warning placeholder."""
        output_path = os.path.join(self.output_dir, "report.pdf")
        try:
            from weasyprint import HTML
            html_content = self.build_html_report(results)
            HTML(string=html_content).write_pdf(output_path)
            logger.info(f"Saved PDF report to {output_path}")
        except Exception as e:
            logger.warning(f"WeasyPrint PDF rendering failed or library not present: {e}. Writing textual PDF placeholder.")
            with open(output_path, "w") as f:
                f.write("WeasyPrint was not configured. Please use HTML/JSON reports.")
        return output_path
