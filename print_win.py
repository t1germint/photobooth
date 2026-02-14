from __future__ import annotations

import logging
import os
import subprocess
from pathlib import Path


def print_image(image_path: Path, printer_name: str | None = None) -> tuple[bool, str]:
    try:
        import win32api  # type: ignore
        import win32print  # type: ignore

        if printer_name:
            win32print.SetDefaultPrinter(printer_name)
        win32api.ShellExecute(0, "print", str(image_path), None, ".", 0)
        return True, "Print command sent via win32 ShellExecute."
    except Exception as exc:  # noqa: BLE001
        logging.warning("Primary printing failed: %s", exc)
        try:
            if os.name == "nt":
                subprocess.Popen(["cmd", "/c", "start", "", str(image_path)], shell=False)
                return False, "Primary print failed; opened image for manual print fallback."
            return False, f"Printing unsupported on this OS: {exc}"
        except Exception as fallback_exc:  # noqa: BLE001
            logging.exception("Printing fallback failed")
            return False, f"Printing failed: {fallback_exc}"
