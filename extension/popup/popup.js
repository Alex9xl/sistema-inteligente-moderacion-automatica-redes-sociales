/**
 * Popup logic - sincroniza la UI con chrome.storage y la pestaña activa.
 */

const els = {
  toggleDeteccion: document.getElementById("toggleDeteccion"),
  statusCard: document.getElementById("statusCard"),
  statusDot: document.getElementById("statusDot"),
  statusTitle: document.getElementById("statusTitle"),
  statusSub: document.getElementById("statusSub"),
  modeGrid: document.getElementById("modeGrid"),
  toggleLexiconBase: document.getElementById("toggleLexiconBase"),
  apiDot: document.getElementById("apiDot"),
  apiText: document.getElementById("apiText"),
  btnPingApi: document.getElementById("btnPingApi"),
  btnRescan: document.getElementById("btnRescan"),
  btnOpenOptions: document.getElementById("btnOpenOptions"),
  statPagina: document.getElementById("statPagina"),
  statTotal: document.getElementById("statTotal"),
  statPalabras: document.getElementById("statPalabras"),
};

document.addEventListener("DOMContentLoaded", init);

async function init() {
  const stored = await chrome.storage.local.get([
    "deteccionActiva",
    "modoCensura",
    "lexiconActivo",
    "palabrasUsuario",
    "apiHabilitada",
    "apiUrl",
    "estadisticas",
  ]);

  const cfg = {
    deteccionActiva: !!stored.deteccionActiva,
    modoCensura: stored.modoCensura || "highlight",
    lexiconActivo: stored.lexiconActivo !== false,
    palabrasUsuario: stored.palabrasUsuario || [],
    apiHabilitada: !!stored.apiHabilitada,
    apiUrl: stored.apiUrl || "http://127.0.0.1:8000",
    estadisticas: stored.estadisticas || { totalDetectados: 0 },
  };

  pintarEstado(cfg);
  bindEventos(cfg);
  pingApi(cfg.apiUrl);
  refrescarStatsPagina();
}

/* ============================================================
 * Pintar estado en la UI
 * ============================================================ */

function pintarEstado(cfg) {
  els.toggleDeteccion.checked = cfg.deteccionActiva;
  els.toggleLexiconBase.checked = cfg.lexiconActivo;
  setEstado(cfg.deteccionActiva);
  setModo(cfg.modoCensura);
  els.statTotal.textContent = formatNumber(
    cfg.estadisticas.totalDetectados || 0
  );
  els.statPalabras.textContent = (cfg.palabrasUsuario || []).length;
}

function setEstado(activo) {
  els.statusCard.classList.toggle("is-on", activo);
  els.statusDot.classList.toggle("is-on", activo);
  els.statusTitle.textContent = activo
    ? "Detección activa"
    : "Detección desactivada";
  els.statusSub.textContent = activo
    ? "Escaneando contenido visible…"
    : "Activa el interruptor para empezar";
}

function setModo(modo) {
  document.querySelectorAll(".mode").forEach((b) => {
    b.classList.toggle("active", b.dataset.modo === modo);
  });
}

/* ============================================================
 * Eventos
 * ============================================================ */

function bindEventos(cfg) {
  els.toggleDeteccion.addEventListener("change", async () => {
    const activo = els.toggleDeteccion.checked;
    await chrome.storage.local.set({ deteccionActiva: activo });
    setEstado(activo);
    if (activo) {
      pedirEscaneo();
    }
  });

  els.toggleLexiconBase.addEventListener("change", async () => {
    await chrome.storage.local.set({
      lexiconActivo: els.toggleLexiconBase.checked,
    });
    pedirEscaneo();
  });

  document.querySelectorAll(".mode").forEach((btn) => {
    btn.addEventListener("click", async () => {
      const modo = btn.dataset.modo;
      await chrome.storage.local.set({ modoCensura: modo });
      setModo(modo);
      pedirEscaneo();
    });
  });

  els.btnRescan.addEventListener("click", () => {
    pedirEscaneo();
    micropulso(els.btnRescan);
  });

  els.btnOpenOptions.addEventListener("click", () => {
    chrome.runtime.openOptionsPage();
  });

  els.btnPingApi.addEventListener("click", () => {
    chrome.storage.local.get(["apiUrl"], (s) => {
      pingApi(s.apiUrl || "http://127.0.0.1:8000");
    });
  });

  // Reaccionar a cambios externos
  chrome.storage.onChanged.addListener((changes) => {
    if (changes.estadisticas) {
      const v = changes.estadisticas.newValue || {};
      els.statTotal.textContent = formatNumber(v.totalDetectados || 0);
    }
    if (changes.palabrasUsuario) {
      els.statPalabras.textContent = (changes.palabrasUsuario.newValue || [])
        .length;
    }
  });
}

/* ============================================================
 * Comunicación con la pestaña activa
 * ============================================================ */

async function pedirEscaneo() {
  try {
    const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
    if (!tab || !tab.id || !esUrlInyectable(tab.url)) return;
    chrome.tabs.sendMessage(tab.id, { tipo: "RESCAN" }, () => {
      // Silenciar lastError cuando la pestaña no tiene content script
      // (chrome://, edge://, páginas de la store, etc.)
      void chrome.runtime.lastError;
      setTimeout(refrescarStatsPagina, 600);
    });
  } catch (_e) {
    /* sin pestaña activa, nada que hacer */
  }
}

function esUrlInyectable(url) {
  if (!url) return false;
  return /^(https?:|file:)/i.test(url);
}

async function refrescarStatsPagina() {
  try {
    const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
    if (!tab || !tab.id || !esUrlInyectable(tab.url)) {
      els.statPagina.textContent = "0";
      return;
    }
    chrome.tabs.sendMessage(tab.id, { tipo: "GET_STATS" }, (resp) => {
      if (chrome.runtime.lastError || !resp) {
        els.statPagina.textContent = "0";
        return;
      }
      els.statPagina.textContent = formatNumber(resp.detectados || 0);
    });
  } catch (_e) {
    els.statPagina.textContent = "0";
  }
}

/* ============================================================
 * Estado de la API (futura)
 * ============================================================ */

function pingApi(url) {
  els.apiDot.classList.remove("is-on", "is-error");
  els.apiText.textContent = "Comprobando…";
  chrome.runtime.sendMessage({ tipo: "PING_API", url }, (res) => {
    if (chrome.runtime.lastError || !res) {
      els.apiDot.classList.add("is-error");
      els.apiText.textContent = "Sin conexión (modo lexicón)";
      return;
    }
    if (res.ok) {
      els.apiDot.classList.add("is-on");
      els.apiText.textContent = "Backend disponible";
    } else {
      els.apiDot.classList.add("is-error");
      els.apiText.textContent = "Sin conexión (modo lexicón)";
    }
  });
}

/* ============================================================
 * Utilidades
 * ============================================================ */

function formatNumber(n) {
  if (n < 1000) return String(n);
  if (n < 1000000) return (n / 1000).toFixed(1).replace(/\.0$/, "") + "k";
  return (n / 1000000).toFixed(1).replace(/\.0$/, "") + "M";
}

function micropulso(el) {
  el.style.transform = "scale(0.96)";
  setTimeout(() => (el.style.transform = ""), 120);
}
