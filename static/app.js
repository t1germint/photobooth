const screens = ["idle", "spin", "reveal", "countdown", "capturing", "preview", "printing", "qr"];
const state = {
  sessionId: null,
  mode: null,
  finalUrl: null,
  operatorMode: false,
  lastSessionId: null,
};

function show(screen) {
  screens.forEach((id) => document.getElementById(id).classList.remove("active"));
  document.getElementById(screen).classList.add("active");
  document.getElementById("status").textContent = `STATE: ${screen.toUpperCase()}`;
}

async function api(path, method = "GET", body = null) {
  const res = await fetch(path, {
    method,
    headers: { "Content-Type": "application/json" },
    body: body ? JSON.stringify(body) : null,
  });
  if (!res.ok) throw new Error(await res.text());
  const ct = res.headers.get("content-type") || "";
  if (ct.includes("application/json")) return res.json();
  return res.text();
}

function wait(ms) { return new Promise(r => setTimeout(r, ms)); }

async function runFlow() {
  try {
    document.getElementById("printError").classList.add("hidden");
    const started = await api("/api/session/start", "POST", {});
    state.sessionId = started.session_id;
    state.lastSessionId = state.sessionId;
    state.mode = started.mode;

    await runSpin();
    await runReveal();
    await runCountdown();
    await runCapture();
    await runPreview();
  } catch (e) {
    console.error(e);
    alert("Something went wrong. Returning to idle.");
    resetIdle();
  }
}

async function runSpin() {
  show("spin");
  const pool = [
    "ICON MODE", "POWER POSE", "SOFT LAUNCH", "BESTIE VIBES", "CAMERA LOVER",
    "SQUAD GOALS", "UNBOTHERED", "PARTY ANIMAL", "MAIN EVENT", "GOLDEN HOUR", "CEO ENERGY"
  ];
  const cells = [...document.querySelectorAll("[data-spin-cell]")];
  const centerIndex = 4;

  cells.forEach((cell, idx) => {
    if (idx !== centerIndex) {
      const interval = setInterval(() => {
        cell.textContent = pool[Math.floor(Math.random() * pool.length)];
      }, 90);
      setTimeout(() => clearInterval(interval), 2500);
    }
  });

  setTimeout(() => {
    cells[centerIndex].textContent = state.mode.name;
  }, 2500);

  if (state.mode.tier === "Legendary") {
    document.getElementById("spin").classList.add("gold");
  }

  await wait(2500);
  document.getElementById("spin").classList.remove("gold");
}

async function runReveal() {
  show("reveal");
  document.getElementById("modeText").textContent = `YOU'RE A ${state.mode.name}!`;
  document.getElementById("modePrompt").textContent = state.mode.prompt || "POSE WITH POWER!";
  await wait(2000);
}

async function runCountdown() {
  show("countdown");
  const n = document.getElementById("countNumber");
  for (const i of [3,2,1]) {
    n.textContent = i;
    await wait(1000);
  }
}

async function runCapture() {
  show("capturing");
  document.getElementById("captureMessage").textContent = "Waiting for camera...";
  document.getElementById("operatorContinue").classList.add("hidden");
  document.getElementById("operatorRestart").classList.add("hidden");
  await api("/api/capture/arm", "POST", { session_id: state.sessionId });

  while (true) {
    await wait(500);
    const s = await api(`/api/capture/status?session_id=${state.sessionId}`);
    if (s.message) document.getElementById("captureMessage").textContent = s.message;

    if (s.state === "captured") {
      const rendered = await api("/api/render/final", "POST", { session_id: state.sessionId });
      state.finalUrl = rendered.final_url + `?t=${Date.now()}`;
      return;
    }
    if (s.state === "error") {
      document.getElementById("operatorContinue").classList.remove("hidden");
      document.getElementById("operatorRestart").classList.remove("hidden");
      return;
    }
  }
}

async function runPreview() {
  show("preview");
  const previewImg = document.getElementById("previewImg");
  if (state.finalUrl) {
    previewImg.src = state.finalUrl;
  } else {
    previewImg.removeAttribute("src");
  }
  const modeLine = document.getElementById("previewModeLine");
  modeLine.textContent = `${state.mode?.name || "SUPERHEROES"}! POWER POSE!`;
  document.getElementById("retakeBtn").classList.toggle("hidden", !state.operatorMode);
}

async function doPrint() {
  show("printing");
  const result = await api("/api/print", "POST", { session_id: state.sessionId });
  if (!result.success) {
    show("preview");
    const err = document.getElementById("printError");
    err.textContent = "Printing failed — tap to retry";
    err.classList.remove("hidden");
    return;
  }
  await showQR();
}

async function showQR() {
  show("qr");
  document.getElementById("qrImg").src = `/api/qr/${state.sessionId}?t=${Date.now()}`;
  setTimeout(resetIdle, 15000);
}

function resetIdle() {
  state.sessionId = null;
  state.mode = null;
  state.finalUrl = null;
  show("idle");
}

document.getElementById("startBtn").addEventListener("click", runFlow);
document.getElementById("printBtn").addEventListener("click", doPrint);
document.getElementById("operatorContinue").addEventListener("click", async () => {
  const rendered = await api("/api/render/final", "POST", { session_id: state.sessionId });
  state.finalUrl = rendered.final_url + `?t=${Date.now()}`;
  runPreview();
});
document.getElementById("operatorRestart").addEventListener("click", resetIdle);
document.getElementById("retakeBtn").addEventListener("click", async () => {
  await runCapture();
  await runPreview();
});

window.addEventListener("keydown", async (e) => {
  if (e.key === "F1" && state.lastSessionId) {
    e.preventDefault();
    await api("/api/print", "POST", { session_id: state.lastSessionId });
  }
  if (e.key === "F2" && state.sessionId) {
    e.preventDefault();
    state.operatorMode = true;
    await runCapture();
    await runPreview();
  }
  if (e.key === "F3" && state.sessionId) {
    e.preventDefault();
    await showQR();
  }
  if (e.key === "F4") {
    e.preventDefault();
    resetIdle();
  }
  if (e.key === "F5") {
    e.preventDefault();
    await api("/api/operator/open-sessions", "POST", {});
  }
});

(async function init() {
  show("idle");
  try {
    const config = await api("/api/config");
    if (!config.incoming_exists) {
      const el = document.getElementById("setupWarn");
      el.textContent = `Setup needed: incoming folder not found at ${config.incoming_folder}`;
      el.classList.remove("hidden");
    }
  } catch (err) {
    console.warn("Config endpoint unavailable; running UI-only preview.", err);
  }

  setInterval(() => {
    const dots = document.getElementById("dots");
    dots.textContent = ".".repeat((dots.textContent.length % 3) + 1);
  }, 450);
})();
