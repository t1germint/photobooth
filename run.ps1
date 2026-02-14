$ErrorActionPreference = "Stop"

$base = "C:\SpinShot"
$dirs = @(
  $base,
  "$base\incoming",
  "$base\sessions",
  "$base\assets",
  "$base\assets\sounds",
  "$base\logs"
)

foreach ($d in $dirs) {
  if (!(Test-Path $d)) { New-Item -ItemType Directory -Path $d | Out-Null }
}

if (!(Test-Path "$base\assets\modes.json")) {
  Copy-Item -Force ".\assets\modes.json" "$base\assets\modes.json"
}
if (!(Test-Path "$base\assets\logo.png")) {
  Copy-Item -Force ".\assets\logo.png" "$base\assets\logo.png"
}

if (!(Test-Path ".\.venv")) {
  py -3.12 -m venv .venv
}

& .\.venv\Scripts\Activate.ps1
pip install -r requirements.txt

Start-Process "http://127.0.0.1:8000"
python -m uvicorn main:app --host 127.0.0.1 --port 8000
