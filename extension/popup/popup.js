/**
 * Popup logic - sincroniza UI, storage y pestana activa.
 */

const UMBRAL_DEFAULT = 0.7;
const API_URL_DEFAULT = "http://127.0.0.1:8000";

const els = {
  toggleDeteccion: document.getElementById("toggleDeteccion"),
  statusCard: document.getElementById("statusCard"),
  statusDot: document.getElementById("statusDot"),
  statusTitle: document.getElementById("statusTitle"),
  statusSub: document.getElementById("statusSub"),
  pageWarning: document.getElementById("pageWarning"),
  pageWarningText: document.getElementById("pageWarningText"),
  modeGrid: document.getElementById("modeGrid"),
  toggleLexiconBase: document.getElementById("toggleLexiconBase"),
  lexiconHint: document.getElementById("lexiconHint"),
  toggleApiPrincipal: document.getElementById("toggleApiPrincipal"),
  apiDot: document.getElementById("apiDot"),
  apiText: document.getElementById("apiText"),
  btnPingApi: document.getElementById("btnPingApi"),
  btnRescan: document.getElementById("btnRescan"),
  btnOpenOptions: document.getElementById("btnOpenOptions"),
  btnResetStats: document.getElementById("btnResetStats"),
  umbralValor: document.getElementById("umbralValor"),
  umbralNivel: document.getElementById("umbralNivel"),
  statPagina: document.getElementById("statPagina"),
  statTotal: document.getElementById("statTotal"),
  statPalabras: document.getElementById("statPalabras"),
  toast: document.getElementById("toast"),
};

document.addEventListener("DOMContentLoaded", init);

function pintarVersion() {
  try {
    const manifest = chrome.runtime.getManifest();
    const version = manifest.version_name || manifest.version || "1.0";
    const el = document.getElementById("version");
    if (el) el.textContent = `v${version}`;
  } catch (_e) {
    /* Si falla, se conserva el texto estático del HTML. */
  }
}

async function init() {
  pintarVersion();
  const stored = await chrome.storage.local.get([
    "deteccionActiva",
    "modoCensura",
    "lexiconActivo",
    "lexiconHabilitado",
    "palabrasUsuario",
    "apiHabilitada",
    "apiUrl",
    "umbralMl",
    "estadisticas",
  ]);

  const cfg = {
    deteccionActiva: !!stored.deteccionActiva,
    modoCensura: stored.modoCensura || "highlight",
    lexiconActivo: stored.lexiconActivo !== false,
    lexiconHabilitado: stored.lexiconHabilitado !== false,
    palabrasUsuario: stored.palabrasUsuario || [],
    apiHabilitada: stored.apiHabilitada !== false,
    apiUrl: stored.apiUrl || API_URL_DEFAULT,
    umbralMl:
      typeof stored.umbralMl === "number" ? stored.umbralMl : UMBRAL_DEFAULT,
    estadisticas: stored.estadisticas || { totalDetectados: 0 },
  };

  pintarEstado(cfg);
  bindEventos();
  await revisarPaginaActual();
  await pingApi(cfg.apiUrl, cfg.apiHabilitada);
  refrescarStatsPagina();
  await verificarMotorActivo();
}

/* ============================================================
 * Salvaguarda: evita que quede sin ningun motor de deteccion
 * ============================================================
 * Si el usuario apaga la API BETO y el lexicon queda sin ningun
 * origen activo (ni diccionario base, ni palabras propias, ni el
 * toggle maestro del lexicon), la extension quedaria "activa" pero
 * sin nada que detectar. Se reactiva el lexicon local como respaldo
 * minimo y se avisa al usuario.
 */
async function verificarMotorActivo() {
  const stored = await chrome.storage.local.get([
    "apiHabilitada",
    "lexiconHabilitado",
    "lexiconActivo",
    "palabrasUsuario",
  ]);

  const apiHabilitada = stored.apiHabilitada !== false;
  const lexiconHabilitado = stored.lexiconHabilitado !== false;
  const lexiconActivo = stored.lexiconActivo !== false;
  const tienePalabrasPropias =
    Array.isArray(stored.palabrasUsuario) && stored.palabrasUsuario.length > 0;

  const lexiconEfectivo = lexiconHabilitado && (lexiconActivo || tienePalabrasPropias);
  const algunMotorActivo = apiHabilitada || lexiconEfectivo;

  if (algunMotorActivo) return;

  await chrome.storage.local.set({
    lexiconHabilitado: true,
    lexiconActivo: true,
  });
  pintarLexicon({ lexiconActivo: true, lexiconHabilitado: true });
  toast(
    "Se reactivó el lexicón local: no puedes desactivar la API BETO y el lexicón al mismo tiempo.",
    "warning"
  );
}

function pintarEstado(cfg) {
  els.toggleDeteccion.checked = cfg.deteccionActiva;
  els.toggleApiPrincipal.checked = cfg.apiHabilitada;
  pintarLexicon(cfg);
  setEstado(cfg);
  setModo(cfg.modoCensura);
  pintarUmbral(cfg.umbralMl);
  els.statTotal.textContent = formatNumber(cfg.estadisticas.totalDetectados || 0);
  els.statPalabras.textContent = (cfg.palabrasUsuario || []).length;
}

/*
 * El diccionario local depende de dos ajustes: el toggle maestro del
 * lexicón (solo editable en Configuración) y el diccionario base. Si el
 * maestro está apagado, aquí se refleja como apagado y no editable, para
 * no mostrar un estado que no corresponde con el comportamiento real.
 */
function pintarLexicon(cfg) {
  const habilitado = cfg.lexiconHabilitado !== false;
  const activo = cfg.lexiconActivo !== false;

  els.toggleLexiconBase.checked = habilitado && activo;
  els.toggleLexiconBase.disabled = !habilitado;

  if (els.lexiconHint) {
    els.lexiconHint.textContent = habilitado
      ? "Se usa si la API no está activa o falla"
      : "Desactivado por completo desde Configuración";
  }
}

function pintarUmbral(valor) {
  const v = typeof valor === "number" && Number.isFinite(valor) ? valor : UMBRAL_DEFAULT;
  if (els.umbralValor) els.umbralValor.textContent = v.toFixed(2);
  if (!els.umbralNivel) return;

  let nivel;
  if (v < 0.5) nivel = "Muy sensible";
  else if (v <= 0.65) nivel = "Equilibrado";
  else nivel = "Estricto";

  els.umbralNivel.textContent =
    Math.abs(v - UMBRAL_DEFAULT) < 0.001 ? `${nivel} · recomendado` : nivel;
}

function setEstado(cfg) {
  const activo = !!cfg.deteccionActiva;
  els.statusCard.classList.toggle("is-on", activo);
  els.statusDot.classList.toggle("is-on", activo);
  els.statusTitle.textContent = activo ? "Extensión activa" : "Extensión desactivada";

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
    const activo = b.dataset.modo === modo;
    b.classList.toggle("active", activo);
    b.setAttribute("aria-pressed", String(activo));
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
    await pingApi(stored.apiUrl || API_URL_DEFAULT, apiHabilitada);
    await verificarMotorActivo();
    pedirEscaneo();
  });

  els.toggleLexiconBase.addEventListener("change", async () => {
    await chrome.storage.local.set({
      lexiconActivo: els.toggleLexiconBase.checked,
    });
    await verificarMotorActivo();
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
    pedirEscaneoConFeedback();
    micropulso(els.btnRescan);
  });

  els.btnOpenOptions.addEventListener("click", () => {
    chrome.runtime.openOptionsPage();
  });

  els.btnPingApi.addEventListener("click", async () => {
    const s = await chrome.storage.local.get(["apiUrl", "apiHabilitada"]);
    pingApi(s.apiUrl || API_URL_DEFAULT, s.apiHabilitada !== false);
  });

  if (els.btnResetStats) {
    els.btnResetStats.addEventListener("click", () => {
      chrome.runtime.sendMessage({ tipo: "RESET_STATS" }, () => {
        void chrome.runtime.lastError;
        els.statTotal.textContent = "0";
        els.statPagina.textContent = "0";
        toast("Contadores reiniciados", "success");
      });
    });
  }

  chrome.storage.onChanged.addListener((changes) => {
    if (changes.estadisticas) {
      const v = changes.estadisticas.newValue || {};
      els.statTotal.textContent = formatNumber(v.totalDetectados || 0);
      refrescarStatsPagina();
    }
    if (changes.palabrasUsuario) {
      els.statPalabras.textContent = (changes.palabrasUsuario.newValue || []).length;
    }
    if (changes.apiHabilitada) {
      els.toggleApiPrincipal.checked = changes.apiHabilitada.newValue !== false;
    }
    if (changes.lexiconActivo || changes.lexiconHabilitado) {
      chrome.storage.local.get(
        ["lexiconActivo", "lexiconHabilitado"],
        (s) => pintarLexicon(s)
      );
    }
    if (changes.umbralMl) {
      pintarUmbral(Number(changes.umbralMl.newValue));
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

async function pedirEscaneoConFeedback() {
  const btn = els.btnRescan;
  if (!btn || btn.disabled) return;

  const textoOriginal = btn.querySelector(".btn-text");
  const labelOriginal = textoOriginal ? textoOriginal.textContent : btn.textContent;

  btn.disabled = true;
  btn.classList.add("is-loading");
  if (textoOriginal) textoOriginal.textContent = "Escaneando…";

  await pedirEscaneo();

  setTimeout(() => {
    btn.disabled = false;
    btn.classList.remove("is-loading");
    if (textoOriginal) textoOriginal.textContent = labelOriginal;
  }, 700);
}

function esUrlInyectable(url) {
  if (!url) return false;
  return /^(https?:|file:)/i.test(url);
}

/*
 * En páginas internas del navegador (chrome://, la tienda de extensiones,
 * PDFs) el content script no puede inyectarse. Sin este aviso el popup
 * mostraba "0" sin explicar por qué la extensión parece no hacer nada.
 */
async function revisarPaginaActual() {
  if (!els.pageWarning) return;

  let url = "";
  try {
    const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
    url = (tab && tab.url) || "";
  } catch (_e) {
    url = "";
  }

  if (esUrlInyectable(url)) {
    els.pageWarning.classList.remove("show");
    return;
  }

  let motivo = "La extensión no puede analizar esta página.";
  if (/^(chrome|edge|about|brave|opera):/i.test(url)) {
    motivo = "Las páginas internas del navegador no se pueden analizar.";
  } else if (/chromewebstore\.google\.com|chrome\.google\.com\/webstore/i.test(url)) {
    motivo = "La tienda de extensiones no permite el análisis.";
  } else if (!url) {
    motivo = "No hay una pestaña web activa para analizar.";
  }

  els.pageWarningText.textContent = motivo;
  els.pageWarning.classList.add("show");
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
      } else if (res.reason === "host_not_allowed") {
        els.apiDot.classList.add("is-error");
        els.apiText.textContent = "URL no permitida; revisa Configuración";
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

let toastTimer;
function toast(msg, kind = "success") {
  if (!els.toast) return;
  els.toast.textContent = msg;
  els.toast.classList.remove("success", "warning", "error");
  els.toast.classList.add(kind);
  els.toast.classList.add("show");
  clearTimeout(toastTimer);
  toastTimer = setTimeout(() => els.toast.classList.remove("show"), 3200);
}
