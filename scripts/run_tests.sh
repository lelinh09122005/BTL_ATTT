#!/bin/bash
# AntiGravity Run Test Suites Script
# --------------------------------------------------

set -e

# Activate venv if present
if [ -d "venv" ]; then
    source venv/bin/activate
fi

echo "=== Running AntiGravity Unit Tests ==="
PYTHONPATH=. pytest tests/unit/ -v --cov=antigravity_framework --cov-report=term-missing

echo "=== Tests completed ==="
