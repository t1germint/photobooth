from __future__ import annotations

import logging
import shutil
import threading
import time
from dataclasses import dataclass
from pathlib import Path
from queue import Empty, Queue

from watchdog.events import FileSystemEvent, FileSystemEventHandler
from watchdog.observers import Observer


@dataclass
class CaptureStatus:
    state: str = "idle"
    raw_path: str | None = None
    message: str = ""
    retries: int = 0


class _IncomingHandler(FileSystemEventHandler):
    def __init__(self, queue: Queue[Path], arm_ts: float) -> None:
        self.queue = queue
        self.arm_ts = arm_ts

    def on_created(self, event: FileSystemEvent) -> None:
        if event.is_directory:
            return
        path = Path(str(event.src_path))
        if path.suffix.lower() in {".jpg", ".jpeg"}:
            self.queue.put(path)


class CaptureWatcher:
    def __init__(self, incoming_folder: Path, max_retries: int = 3, timeout_seconds: int = 8) -> None:
        self.incoming_folder = incoming_folder
        self.max_retries = max_retries
        self.timeout_seconds = timeout_seconds

        self._statuses: dict[str, CaptureStatus] = {}
        self._threads: dict[str, threading.Thread] = {}

    def arm_session(self, session_id: str, raw_destination: Path) -> CaptureStatus:
        status = CaptureStatus(state="waiting", message="Waiting for DSLR image...")
        self._statuses[session_id] = status

        arm_ts = time.time()
        thread = threading.Thread(
            target=self._wait_for_new_file,
            args=(session_id, arm_ts, raw_destination),
            daemon=True,
        )
        self._threads[session_id] = thread
        thread.start()
        return status

    def status(self, session_id: str) -> CaptureStatus:
        return self._statuses.get(session_id, CaptureStatus(state="idle", message="Session not armed."))

    def _wait_for_new_file(self, session_id: str, arm_ts: float, raw_destination: Path) -> None:
        status = self._statuses[session_id]

        if not self.incoming_folder.exists():
            status.state = "error"
            status.message = f"Incoming folder not found: {self.incoming_folder}"
            return

        event_queue: Queue[Path] = Queue()
        handler = _IncomingHandler(event_queue, arm_ts)
        observer = Observer()
        observer.schedule(handler, str(self.incoming_folder), recursive=False)
        observer.start()

        retries = 0
        try:
            while retries <= self.max_retries:
                candidate = self._find_newest_after(arm_ts)

                if candidate is None:
                    try:
                        event_file = event_queue.get(timeout=0.4)
                        if event_file.exists() and event_file.stat().st_mtime >= arm_ts:
                            candidate = event_file
                    except Empty:
                        candidate = None

                if candidate:
                    try:
                        time.sleep(0.2)
                        shutil.copy2(candidate, raw_destination)
                        status.state = "captured"
                        status.raw_path = str(raw_destination)
                        status.message = "Capture received"
                        logging.info("Captured image for session %s from %s", session_id, candidate)
                        return
                    except Exception as exc:  # noqa: BLE001
                        status.state = "error"
                        status.message = f"Failed to copy capture: {exc}"
                        logging.exception("Copy failed for session %s", session_id)
                        return

                elapsed = time.time() - arm_ts
                current_window = (retries + 1) * self.timeout_seconds
                if elapsed >= current_window:
                    retries += 1
                    status.retries = retries
                    if retries <= self.max_retries:
                        status.message = "RETRYING..."
                        logging.warning("Capture retry %s for session %s", retries, session_id)
                    else:
                        status.state = "error"
                        status.message = "No photo received. Ask operator for help."
                        logging.error("Capture timed out for session %s", session_id)
                        return
        finally:
            observer.stop()
            observer.join(timeout=1.0)

    def _find_newest_after(self, arm_ts: float) -> Path | None:
        newest: tuple[float, Path] | None = None
        for path in self.incoming_folder.iterdir():
            if path.suffix.lower() not in {".jpg", ".jpeg"}:
                continue
            try:
                mtime = path.stat().st_mtime
            except FileNotFoundError:
                continue
            if mtime >= arm_ts:
                if newest is None or mtime > newest[0]:
                    newest = (mtime, path)
        return newest[1] if newest else None
