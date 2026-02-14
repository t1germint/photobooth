from __future__ import annotations

import json
import logging
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any


@dataclass
class SessionPaths:
    session_id: str
    session_dir: Path
    raw_path: Path
    final_path: Path
    mode_path: Path
    qr_path: Path


class SessionManager:
    def __init__(self, base_path: Path) -> None:
        self.base_path = base_path
        self.sessions_path = base_path / "sessions"

    def create_session(self, mode: dict[str, Any]) -> SessionPaths:
        session_id = datetime.now().strftime("%Y-%m-%d_%H%M%S")
        session_dir = self.sessions_path / session_id
        session_dir.mkdir(parents=True, exist_ok=True)

        paths = SessionPaths(
            session_id=session_id,
            session_dir=session_dir,
            raw_path=session_dir / "raw.jpg",
            final_path=session_dir / "final.jpg",
            mode_path=session_dir / "mode.json",
            qr_path=session_dir / "qr.png",
        )
        paths.mode_path.write_text(json.dumps(mode, indent=2), encoding="utf-8")
        return paths

    def get_session_paths(self, session_id: str) -> SessionPaths:
        session_dir = self.sessions_path / session_id
        return SessionPaths(
            session_id=session_id,
            session_dir=session_dir,
            raw_path=session_dir / "raw.jpg",
            final_path=session_dir / "final.jpg",
            mode_path=session_dir / "mode.json",
            qr_path=session_dir / "qr.png",
        )

    def load_mode(self, session_id: str) -> dict[str, Any]:
        mode_path = self.sessions_path / session_id / "mode.json"
        if not mode_path.exists():
            return {}
        try:
            return json.loads(mode_path.read_text(encoding="utf-8"))
        except Exception as exc:  # noqa: BLE001
            logging.exception("Failed to load mode.json for %s: %s", session_id, exc)
            return {}
