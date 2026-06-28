import sys
from pathlib import Path

import uvicorn

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
sys.path.insert(0, str(SRC))

uvicorn.run("ui.backend.app:app", host="127.0.0.1", port=8080)
