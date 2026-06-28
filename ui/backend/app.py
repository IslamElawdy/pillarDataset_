from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

ROOT = Path(__file__).resolve().parents[2]
FRONTEND = ROOT / "ui" / "frontend"

app = FastAPI(title="AutoWert Synthetic Dataset UI")
app.mount("/static", StaticFiles(directory=str(FRONTEND)), name="static")


@app.get("/")
def index():
    return FileResponse(str(FRONTEND / "index.html"))


@app.get("/api/status")
def status():
    return {"ok": True, "project_root": str(ROOT)}
