# SpinShot (Windows Local Photobooth)

SpinShot is an offline local kiosk photobooth app for Windows. It uses a fullscreen browser UI + Python backend, watches a Canon EOS Utility hot-folder, renders a 4x6 print image, prints it, and shows a QR download screen.

## Stack
- Python 3.12+
- FastAPI backend
- HTML/CSS/JS single-page frontend
- watchdog for hot-folder monitoring
- Pillow for render pipeline
- qrcode for QR creation
- pywin32 printing with fallback

## Folder layout
SpinShot runtime paths (created under `C:\SpinShot`):
- `incoming\` (Canon EOS Utility destination)
- `sessions\YYYY-MM-DD_HHMMSS\raw.jpg/final.jpg/mode.json/qr.png`
- `assets\logo.png`, `assets\modes.json`
- `logs\app.log`

## Setup
1. Install Python 3.12+ on Windows.
2. Clone this repo.
3. Configure Canon EOS Utility tethering destination to:
   - `C:\SpinShot\incoming\`
4. Optional: set preferred printer in env var:
   - `SPINSHOT_PRINTER_NAME="Your Printer Name"`
5. Run:
   - Right click PowerShell > Run as normal user
   - `./run.ps1`

This script will create folders, install dependencies, copy default assets, launch the API server, and open browser at `http://127.0.0.1:8000`.

## Kiosk mode
Use browser fullscreen (`F11`) or Windows kiosk shell if desired. UI supports touchscreen + mouse.

## Workflow states
`IDLE -> SPIN -> REVEAL -> COUNTDOWN -> CAPTURING -> PREVIEW -> PRINTING -> QR -> IDLE`

Operator hotkeys:
- `F1` Reprint last final
- `F2` Retake (re-arm capture)
- `F3` Skip to QR
- `F4` Restart to idle
- `F5` Open sessions folder in Explorer

## API
- `POST /api/session/start`
- `POST /api/capture/arm`
- `GET /api/capture/status?session_id=`
- `POST /api/render/final`
- `POST /api/print`
- `GET /api/qr/{session_id}`
- `GET /download/{session_id}`
- `GET /health`

## Notes
- If printer integration fails, SpinShot opens fallback viewer path and allows retry from UI.
- If no image arrives after retries, operator override buttons appear.
- Render output is fixed 1800x1200 with a solid white bottom bar and only MODE text + logo.

## React arcade UI demo (new)
A neon/comic 7-state flow demo lives in `frontend/`.

### Run
1. `cd frontend`
2. `npm install`
3. `npm run dev`
4. Open the printed local URL.

### Tweak timings and modes
- State timings and transitions: `frontend/src/PhotoboothFlow.tsx`
- Mode list: `frontend/src/types.ts` (`MODES`)
- Screen visuals/components: `frontend/src/screens/*`
- Global arcade styling: `frontend/src/styles/photobooth.css`
