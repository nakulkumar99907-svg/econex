"""
ECONEX Combined Runner
Starts the integrated Frontend + Backend + SQLite Database service.
"""

import sys
from pathlib import Path

# Add backend directory to path
ROOT_DIR = Path(__file__).resolve().parent
BACKEND_DIR = ROOT_DIR / "backend"
sys.path.insert(0, str(BACKEND_DIR))

import main

if __name__ == "__main__":
    main.run_server(host="127.0.0.1", port=8000)
