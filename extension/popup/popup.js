/**
 * Popup logic - sincroniza UI, storage y pestana activa.
 */

const els = {
  toggleDeteccion: document.getElementById("toggleDeteccion"),
  statusCard: document.getElementById("statusCard"),
  statusDot: document.getElementById("statusDot"),
  statusTitle: document.getElementById("statusTitle"),
  statusSub: document.getElementById("statusSub"),
  modeGrid: document.getElementById("modeGrid"),
  toggleLexiconBase: document.getElementById("toggleLexiconBase"),
  toggleApiPrincipal: document.getElementById("toggleApiPrincipal"),
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
    apiHabilitada: stored.apiHabilitada !== false,
    apiUrl: stored.apiUrl || "http://127.0.0.1:8000",
    estadisticas: stored.estadisticas || { totalDetectados: 0 },
  };

  pintarEstado(cfg);
  bindEventos();
  await pingApi(cfg.apiUrl, cfg.apiHabilitada);
  refrescarStatsPagina();
}

function pintarEstado(cfg) {
  els.toggleDeteccion.checked = cfg.deteccionActiva;
  els.toggleLexiconBase.checked = cfg.lexiconActivo;
  els.toggleApiPrincipal.checked = cfg.apiHabilitada;
  setEstado(cfg);
  setModo(cfg.modoCensura);
  els.statTotal.textContent = formatNumber(cfg.estadisticas.totalDetectados || 0);
  els.statPalabras.textContent = (cfg.palabrasUsuario || []).length;
}

function setEstado(cfg) {
  const activo = !!cfg.deteccionActiva;
  els.statusCard.classList.toggle("is-on", activo);
  els.statusDot.classList.toggle("is-on", activo);
  els.statusTitle.textContent = activo ? "Detección activa" : "Detección desactivada";

  if (!activo) {
    els.statusSub.textContent = "Activa el interruptor para empezar";
  } else if (cfg.apiHabilitada) {
    els.statusSub.textContent = "API BETO prioritaria";
  } else {
    els.statusSub.textContent = "Modo lexicón de respaldo";
  }
}

function setModo(modo) {
  document.querySelectorAll(".mode").forEach((b) => {
    b.classList.toggle("active", b.dataset.modo === modo);
  });
}

function bindEventos() {
  els.toggleDeteccion.addEventListener("change", async () => {
    const activo = els.toggleDeteccion.checked;
    const stored = await chrome.storage.local.get(["apiHabilitada"]);
    await chrome.storage.local.set({ deteccionActiva: activo });
    setEstado({ deteccionActiva: activo, apiHabilitada: stored.apiHabilitada !== false });
    if (activo) pedirEscaneo();
  });

  els.toggleApiPrincipal.addEventListener("change", async () => {
    const apiHabilitada = els.toggleApiPrincipal.checked;
    await chrome.storage.local.set({ apiHabilitada });
    const stored = await chrome.storage.local.get(["deteccionActiva", "apiUrl"]);
    setEstado({ deteccionActiva: !!stored.deteccionActiva, apiHabilitada });
    await pingApi(stored.apiUrl || "http://127.0.0.1:8000", apiHabilitada);
    pedirEscaneo();
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

  els.btnPingApi.addEventListener("click", async () => {
    const s = await chrome.storage.local.get(["apiUrl", "apiHabilitada"]);
    pingApi(s.apiUrl || "http://127.0.0.1:8000", s.apiHabilitada !== false);
  });

  chrome.storage.onChanged.addListener((changes) => {
    if (changes.estadisticas) {
      const v = changes.estadisticas.newValue || {};
      els.statTotal.textContent = formatNumber(v.totalDetectados || 0);
    }
    if (changes.palabrasUsuario) {
      els.statPalabras.textContent = (changes.palabrasUsuario.newValue || []).length;
    }
    if (changes.apiHabilitada) {
      els.toggleApiPrincipal.checked = changes.apiHabilitada.newValue !== false;
    }
    if (changes.lexiconActivo) {
      els.toggleLexiconBase.checked = changes.lexiconActivo.newValue !== false;
    }
  });
}

async function pedirEscaneo() {
  try {
    const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
    if (!tab || !tab.id || !esUrlInyectable(tab.url)) return;
    chrome.tabs.sendMessage(tab.id, { tipo: "RESCAN" }, () => {
      void chrome.runtime.lastError;
      setTimeout(refrescarStatsPagina, 700);
    });
  } catch (_e) {
    /* sin pestana activa */
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

function pingApi(url, apiHabilitada = true) {
  els.apiDot.classList.remove("is-on", "is-error", "is-warn");

  if (!apiHabilitada) {
    els.apiDot.classList.add("is-warn");
    els.apiText.textContent = "API desactivada; usando lexicón";
    return Promise.resolve();
  }

  els.apiText.textContent = "Comprobando modelo...";
  return new Promise((resolve) => {
    chrome.runtime.sendMessage({ tipo: "PING_API", url }, (res) => {
      if (chrome.runtime.lastError || !res) {
        els.apiDot.classList.add("is-error");
        els.apiText.textContent = "API sin conexión; respaldo local";
        resolve();
        return;
      }

      if (res.ok) {
        els.apiDot.classList.add("is-on");
        els.apiText.textContent = "API BETO lista";
      } else if (res.reason === "model_not_loaded") {
        els.apiDot.classList.add("is-error");
        els.apiText.textContent = "API sin modelo cargado";
      } else {
        els.apiDot.classList.add("is-error");
        els.apiText.textContent = "API sin conexión; respaldo local";
      }
      resolve();
    });
  });
}

function formatNumber(n) {
  if (n < 1000) return String(n);
  if (n < 1000000) return (n / 1000).toFixed(1).replace(/\.0$/, "") + "k";
  return (n / 1000000).toFixed(1).replace(/\.0$/, "") + "M";
}

function micropulso(el) {
  el.style.transform = "scale(0.96)";
  setTimeout(() => (el.style.transform = ""), 120);
}
