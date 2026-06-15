import os
import uvicorn
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from loguru import logger

class DashboardServer:
    def __init__(self, report_dir: str = "./reports"):
        self.report_dir = report_dir
        self.app = FastAPI(title="AntiGravity Web Dashboard")
        self.setup_routes()

    def setup_routes(self):
        @self.app.get("/", response_class=HTMLResponse)
        async def read_dashboard():
            report_path = os.path.join(self.report_dir, "report.html")
            if os.path.exists(report_path):
                with open(report_path, "r", encoding="utf-8") as f:
                    return f.read()
            return """
            <html>
                <body style="font-family: sans-serif; background-color: #0f172a; color: white; text-align: center; padding-top: 100px;">
                    <h1>No AntiGravity report found.</h1>
                    <p>Run a security scan to generate reports first.</p>
                </body>
            </html>
            """

    def start(self, host: str = "127.0.0.1", port: int = 8080):
        logger.info(f"Starting AntiGravity dashboard server on http://{host}:{port}")
        uvicorn.run(self.app, host=host, port=port)
