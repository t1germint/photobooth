from __future__ import annotations

import json
import logging
import os
import random
import subprocess
from pathlib import Path
from typing import Any

import qrcode
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from camera_hotfolder import CaptureWatcher
from print_win import print_image
from render import BAR_HEIGHT, TARGET_H, TARGET_W, render_final
from sessions import SessionManager

# ===== Config =====
BASE_PATH = Path(r"C:\SpinShot")
INCOMING_FOLDER = BASE_PATH / "incoming"
SESSIONS_FOLDER = BASE_PATH / "sessions"
ASSETS_FOLDER = BASE_PATH / "assets"
LOGS_FOLDER = BASE_PATH / "logs"
LOG_FILE = LOGS_FOLDER / "app.log"
MODES_PATH = ASSETS_FOLDER / "modes.json"
LOGO_PATH = ASSETS_FOLDER / "logo.png"
FONT_PATH = ASSETS_FOLDER / "fonts" / "Inter-Bold.ttf"
PRINTER_NAME = os.getenv("SPINSHOT_PRINTER_NAME")
SERVER_URL = os.getenv("SPINSHOT_SERVER_URL", "http://127.0.0.1:8000")


def setup_logging() -> None:
    LOGS_FOLDER.mkdir(parents=True, exist_ok=True)
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        handlers=[logging.FileHandler(LOG_FILE, encoding="utf-8"), logging.StreamHandler()],
    )


def ensure_folders() -> None:
    for p in [BASE_PATH, INCOMING_FOLDER, SESSIONS_FOLDER, ASSETS_FOLDER, LOGS_FOLDER, ASSETS_FOLDER / "sounds"]:
        p.mkdir(parents=True, exist_ok=True)


def load_modes() -> list[dict[str, Any]]:
    if not MODES_PATH.exists():
        raise FileNotFoundError(f"Missing modes file: {MODES_PATH}")
    return json.loads(MODES_PATH.read_text(encoding="utf-8"))


def pick_mode(modes: list[dict[str, Any]]) -> dict[str, Any]:
    tiers = {
        "Common": 0.70,
        "Spicy": 0.25,
        "Legendary": 0.05,
    }
    picked_tier = random.choices(list(tiers.keys()), weights=list(tiers.values()), k=1)[0]
    tier_modes = [m for m in modes if m.get("tier") == picked_tier]
    if not tier_modes:
        tier_modes = modes
    weights = [max(1, int(m.get("weight", 1))) for m in tier_modes]
    return random.choices(tier_modes, weights=weights, k=1)[0]


class SessionStartResponse(BaseModel):
    session_id: str
    mode: dict[str, Any]


class SessionRequest(BaseModel):
    session_id: str


class RenderRequest(BaseModel):
    session_id: str


class CaptureState(BaseModel):
    state: str
    raw_path: str | None = None
    message: str = ""
    retries: int = 0


setup_logging()
ensure_folders()
session_manager = SessionManager(BASE_PATH)
capture_watcher = CaptureWatcher(INCOMING_FOLDER, max_retries=3, timeout_seconds=8)
app = FastAPI(title="SpinShot")
app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/", response_class=HTMLResponse)
def index() -> str:
    return (Path("static") / "index.html").read_text(encoding="utf-8")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/api/session/start", response_model=SessionStartResponse)
def start_session() -> SessionStartResponse:
    modes = load_modes()
    mode = pick_mode(modes)
    paths = session_manager.create_session(mode)
    logging.info("Session started: %s (%s)", paths.session_id, mode.get("name"))
    return SessionStartResponse(session_id=paths.session_id, mode=mode)


@app.post("/api/capture/arm")
def arm_capture(payload: SessionRequest) -> dict[str, Any]:
    paths = session_manager.get_session_paths(payload.session_id)
    status = capture_watcher.arm_session(payload.session_id, paths.raw_path)
    return {"armed": True, "state": status.state}


@app.get("/api/capture/status", response_model=CaptureState)
def capture_status(session_id: str) -> CaptureState:
    s = capture_watcher.status(session_id)
    return CaptureState(state=s.state, raw_path=s.raw_path, message=s.message, retries=s.retries)


@app.post("/api/render/final")
def render_final_api(payload: RenderRequest) -> dict[str, str]:
    paths = session_manager.get_session_paths(payload.session_id)
    if not paths.raw_path.exists():
        raise HTTPException(status_code=404, detail="raw.jpg not found")
    mode = session_manager.load_mode(payload.session_id)
    mode_name = mode.get("name", "SPINSHOT")
    output = render_final(paths.raw_path, paths.final_path, mode_name, LOGO_PATH, FONT_PATH)
    return {"final_path": str(output), "final_url": f"/sessions/{payload.session_id}/final.jpg"}


@app.post("/api/print")
def print_api(payload: SessionRequest) -> dict[str, Any]:
    paths = session_manager.get_session_paths(payload.session_id)
    if not paths.final_path.exists():
        raise HTTPException(status_code=404, detail="final.jpg not found")
    success, message = print_image(paths.final_path, PRINTER_NAME)
    logging.info("Print for %s success=%s message=%s", payload.session_id, success, message)
    return {"success": success, "message": message}


@app.get("/api/qr/{session_id}")
def qr_api(session_id: str) -> FileResponse:
    paths = session_manager.get_session_paths(session_id)
    if not paths.qr_path.exists():
        download_url = f"{SERVER_URL}/download/{session_id}"
        qr_img = qrcode.make(download_url)
        qr_img.save(paths.qr_path)
    return FileResponse(paths.qr_path)


@app.get("/download/{session_id}", response_class=HTMLResponse)
def download_page(session_id: str) -> str:
    paths = session_manager.get_session_paths(session_id)
    if not paths.final_path.exists():
        raise HTTPException(status_code=404, detail="Photo not found")
    return f"""
    <html><body style='background:#111;color:white;font-family:Arial;padding:40px'>
    <h1>SpinShot Download</h1>
    <p>Your photo is ready.</p>
    <a href='/sessions/{session_id}/final.jpg' download style='color:#7cff00;font-size:24px'>Download final.jpg</a>
    </body></html>
    """


@app.get("/sessions/{session_id}/final.jpg")
def final_file(session_id: str) -> FileResponse:
    path = session_manager.get_session_paths(session_id).final_path
    if not path.exists():
        raise HTTPException(status_code=404, detail="final.jpg missing")
    return FileResponse(path)


@app.post("/api/operator/open-sessions")
def open_sessions() -> dict[str, str]:
    try:
        subprocess.Popen(["explorer.exe", str(SESSIONS_FOLDER)])
        return {"status": "opened"}
    except Exception as exc:  # noqa: BLE001
        return {"status": f"failed: {exc}"}


@app.get("/api/config")
def config_api() -> dict[str, Any]:
    return {
        "incoming_exists": INCOMING_FOLDER.exists(),
        "incoming_folder": str(INCOMING_FOLDER),
        "canvas": {"width": TARGET_W, "height": TARGET_H, "bar_height": BAR_HEIGHT},
    }
