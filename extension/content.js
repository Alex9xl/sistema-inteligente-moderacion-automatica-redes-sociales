/**
 * Content script - Detector ES v1.0.
 *
 * Flujo operativo:
 *   1. Si la API BETO esta habilitada y no esta en cooldown, se envian
 *      fragmentos visibles al backend local y se censuran los resultados
 *      que superan el umbral configurado.
 *   2. Si la API esta deshabilitada, sin modelo cargado o falla, se activa
 *      el lexicon local como respaldo controlado.
 *   3. Un reintento de salud intenta volver a la API sin exigir recarga.
 */

const SCAN_DEBOUNCE_MS = 500;
const MAX_NODOS_POR_ESCANEO = 5000;
const MAX_ML_FRAGMENTOS_POR_ESCANEO = 80;
const MIN_ML_CHARS = 15;
const MAX_ML_CHARS = 512;
const API_RETRY_MS = 30000;
const MAX_REFS_ML = 400;

const HATE_MARK_CLASS = "hate-detect-mark";
const HATE_NODE_FLAG = "data-hate-scanned";
const ML_MARK_CLASS = "hate-ml-mark";
const ML_ID_ATTR = "data-hate-ml-id";
const ML_STATE_ATTR = "data-hate-ml-state";

const config = {
  activo: false,
  modo: "highlight", // highlight | blur | asterisk | hide
  apiHabilitada: true,
  apiDisponible: null,
  apiFallbackHasta: 0,
  apiUrl: "http://127.0.0.1:8000",
  umbralMl: 0.7,
  lexiconUsuario: [],
  lexiconActivo: true,
  lexiconHabilitado: true, // toggle maestro del lexicón (options page)
  detectados: 0,
};

if (!window.__hateRefs) window.__hateRefs = {};

let regexActiva = null;
let observer = null;
let debounceTimer = null;
let apiRetryTimer = null;
let scanInProgress = false;

(async function init() {
  const stored = await chrome.storage.local.get([
    "deteccionActiva",
    "modoCensura",
    "palabrasUsuario",
    "lexiconActivo",
    "lexiconHabilitado",
    "apiHabilitada",
    "umbralMl",
    "apiUrl",
  ]);

  config.activo = !!stored.deteccionActiva;
  config.modo = stored.modoCensura || "highlight";
  config.lexiconUsuario = Array.isArray(stored.palabrasUsuario)
    ? stored.palabrasUsuario
    : [];
  config.lexiconActivo = stored.lexiconActivo !== false;
  config.lexiconHabilitado = stored.lexiconHabilitado !== false;
  config.apiHabilitada = stored.apiHabilitada !== false;
  config.umbralMl = typeof stored.umbralMl === "number" ? stored.umbralMl : 0.7;
  config.apiUrl = stored.apiUrl || "http://127.0.0.1:8000";

  rebuildRegex();

  if (config.activo) {
    activar();
  }
})();

chrome.storage.onChanged.addListener((changes) => {
  let needRebuild = false;
  let needCleanRescan = false;

  if (changes.deteccionActiva) {
    config.activo = !!changes.deteccionActiva.newValue;
    if (config.activo) activar();
    else desactivar();
  }

  if (changes.modoCensura) {
    config.modo = changes.modoCensura.newValue || "highlight";
    needCleanRescan = true;
  }

  if (changes.palabrasUsuario) {
    config.lexiconUsuario = Array.isArray(changes.palabrasUsuario.newValue)
      ? changes.palabrasUsuario.newValue
      : [];
    needRebuild = true;
  }

  if (changes.lexiconActivo) {
    config.lexiconActivo = changes.lexiconActivo.newValue !== false;
    needRebuild = true;
  }

  if (changes.lexiconHabilitado) {
    config.lexiconHabilitado = changes.lexiconHabilitado.newValue !== false;
    needRebuild = true;
  }

  if (changes.apiHabilitada) {
    config.apiHabilitada = changes.apiHabilitada.newValue !== false;
    config.apiDisponible = null;
    config.apiFallbackHasta = 0;
    clearTimeout(apiRetryTimer);
    needCleanRescan = true;
  }

  if (changes.umbralMl) {
    config.umbralMl =
      typeof changes.umbralMl.newValue === "number"
        ? changes.umbralMl.newValue
        : 0.7;
    needCleanRescan = true;
  }

  if (changes.apiUrl) {
    config.apiUrl = changes.apiUrl.newValue || "http://127.0.0.1:8000";
    config.apiDisponible = null;
    config.apiFallbackHasta = 0;
    clearTimeout(apiRetryTimer);
    needCleanRescan = true;
  }

  if (needRebuild) rebuildRegex();

  if ((needRebuild || needCleanRescan) && config.activo) {
    reiniciarEscaneoCompleto();
    scheduleScan(0);
  }
});

chrome.runtime.onMessage.addListener((msg, _sender, sendResponse) => {
  if (!msg || !msg.tipo) return false;

  if (msg.tipo === "GET_STATS") {
    sendResponse({
      detectados: config.detectados,
      activo: config.activo,
      apiHabilitada: config.apiHabilitada,
      apiDisponible: config.apiDisponible,
      ruta: rutaActiva(),
    });
    return true;
  }

  if (msg.tipo === "RESCAN") {
    if (config.activo) {
      reiniciarEscaneoCompleto();
      scheduleScan(0);
    }
    sendResponse({ ok: true });
    return true;
  }

  if (msg.tipo === "RESULTADO") {
    aplicarResultadoML(msg);
    sendResponse({ ok: true });
    return true;
  }

  if (msg.tipo === "API_STATUS") {
    manejarEstadoApi(msg);
    sendResponse({ ok: true });
    return true;
  }

  if (msg.tipo === "API_UNAVAILABLE") {
    manejarApiNoDisponible(msg);
    sendResponse({ ok: true });
    return true;
  }

  if (msg.tipo === "EXPLAIN_RES") {
    aplicarExplicacion(msg);
    sendResponse({ ok: true });
    return true;
  }

  return false;
});

function activar() {
  if (!document.body) {
    setTimeout(activar, 100);
    return;
  }

  conectarObserver();
  scheduleScan(0);
}

function conectarObserver() {
  if (!config.activo || !document.body) return;
  if (!observer) {
    observer = new MutationObserver(() => scheduleScan());
  }
  observer.observe(document.body, { childList: true, subtree: true });
}

/*
 * Al insertar las marcas se modifica el DOM, lo que volveria a disparar el
 * propio MutationObserver y generaria escaneos en cascada. Se pausa la
 * observacion mientras se aplican los cambios y se reanuda despues.
 */
function conMutacionesPausadas(fn) {
  const observaba = !!observer;
  if (observaba) observer.disconnect();
  try {
    return fn();
  } finally {
    if (observaba) conectarObserver();
  }
}

function desactivar() {
  if (observer) {
    observer.disconnect();
    observer = null;
  }
  clearTimeout(debounceTimer);
  clearTimeout(apiRetryTimer);
  limpiarMarcas();
  limpiarEstadoMl();
  config.detectados = 0;
  enviarStats();
}

function scheduleScan(delay = SCAN_DEBOUNCE_MS) {
  if (!config.activo) return;
  clearTimeout(debounceTimer);
  debounceTimer = setTimeout(() => {
    debounceTimer = null;
    escanear();
  }, delay);
}

function rutaActiva() {
  if (debeUsarApi()) return "api";
  return "lexicon";
}

function debeUsarApi() {
  return config.apiHabilitada && Date.now() >= config.apiFallbackHasta;
}

function rebuildRegex() {
  // Si el toggle maestro del lexicón está apagado, no construir nada.
  if (!config.lexiconHabilitado) {
    regexActiva = null;
    return;
  }

  const lista = [];
  if (config.lexiconActivo && typeof self.lexiconBuildDefaultSet === "function") {
    lista.push(...self.lexiconBuildDefaultSet());
  }
  if (Array.isArray(config.lexiconUsuario)) {
    lista.push(...config.lexiconUsuario);
  }

  const unicos = Array.from(
    new Set(
      lista
        .filter((t) => typeof t === "string")
        .map((t) => t.toLowerCase().trim())
        .filter(Boolean)
    )
  );

  regexActiva =
    typeof self.lexiconBuildRegex === "function"
      ? self.lexiconBuildRegex(unicos)
      : null;
}

function escanear() {
  if (!config.activo || !document.body || scanInProgress) return;
  scanInProgress = true;

  try {
    if (debeUsarApi()) {
      // BUG3: proteger recolectarFragmentosML para que un error interno
      // no bloquee scanInProgress de forma permanente.
      let fragmentos;
      try {
        fragmentos = recolectarFragmentosML();
      } catch (_e) {
        fragmentos = [];
      }

      if (fragmentos.length > 0) {
        enviarLoteAlModelo(fragmentos);
        return;
      }

      // BUG1: si no hay fragmentos nuevos para la API (todos ya marcados),
      // ejecutar lexicón como complemento para cubrir términos personales
      // y texto corto por debajo del umbral MIN_ML_CHARS.
      try {
        escanearLexicon();
      } catch (_e) { /* walker fallo — continuar sin bloquear */ }
      return;
    }

    escanearLexicon();
  } catch (_e) {
    /* BUG3: capturar errores inesperados para liberar scanInProgress */
  } finally {
    scanInProgress = false;
  }
}

function escanearLexicon() {
  if (!regexActiva) return;

  let nuevasDetecciones = 0;
  const walker = document.createTreeWalker(
    document.body,
    NodeFilter.SHOW_TEXT,
    {
      acceptNode(node) {
        const parent = node.parentElement;
        if (!esNodoTextoProcesable(node, parent)) return NodeFilter.FILTER_REJECT;
        if (parent.closest(`.${HATE_MARK_CLASS}`)) return NodeFilter.FILTER_REJECT;
        if (parent.hasAttribute(HATE_NODE_FLAG)) return NodeFilter.FILTER_REJECT;
        return NodeFilter.FILTER_ACCEPT;
      },
    }
  );

  const objetivos = [];
  let visitados = 0;
  let n;
  while ((n = walker.nextNode())) {
    visitados += 1;
    if (visitados > MAX_NODOS_POR_ESCANEO) break;
    regexActiva.lastIndex = 0;
    if (regexActiva.test(n.nodeValue)) {
      regexActiva.lastIndex = 0;
      objetivos.push(n);
    }
  }

  conMutacionesPausadas(() => {
    for (const textNode of objetivos) {
      nuevasDetecciones += procesarNodoTexto(textNode);
    }
  });

  if (nuevasDetecciones > 0) {
    config.detectados += nuevasDetecciones;
    enviarStats();
  }
}

function recolectarFragmentosML() {
  const fragmentos = [];
  const walker = document.createTreeWalker(
    document.body,
    NodeFilter.SHOW_TEXT,
    {
      acceptNode(node) {
        const parent = node.parentElement;
        if (!esNodoTextoProcesable(node, parent)) return NodeFilter.FILTER_REJECT;
        if (parent.closest(`.${HATE_MARK_CLASS}, .hate-explain-token`)) {
          return NodeFilter.FILTER_REJECT;
        }
        if (parent.closest(`[${ML_STATE_ATTR}]`)) return NodeFilter.FILTER_REJECT;
        if (!esVisible(parent)) return NodeFilter.FILTER_REJECT;

        const texto = normalizarTextoParaApi(node.nodeValue);
        if (texto.length < MIN_ML_CHARS) return NodeFilter.FILTER_REJECT;
        return NodeFilter.FILTER_ACCEPT;
      },
    }
  );

  let visitados = 0;
  let node;
  while ((node = walker.nextNode())) {
    visitados += 1;
    if (visitados > MAX_NODOS_POR_ESCANEO) break;
    if (fragmentos.length >= MAX_ML_FRAGMENTOS_POR_ESCANEO) break;

    const parent = node.parentElement;
    const texto = normalizarTextoParaApi(node.nodeValue);
    if (!parent || texto.length < MIN_ML_CHARS) continue;

    const id = crearMlId();
    parent.setAttribute(ML_ID_ATTR, id);
    parent.setAttribute(ML_STATE_ATTR, "pending");
    window.__hateRefs[id] = {
      node,
      parent,
      texto,
      original: node.nodeValue || "",
    };
    fragmentos.push({ id, texto });
  }

  return fragmentos;
}

function esNodoTextoProcesable(node, parent) {
  if (!node || !parent) return false;
  const tag = parent.tagName;
  if (
    [
      "SCRIPT",
      "STYLE",
      "NOSCRIPT",
      "TEXTAREA",
      "INPUT",
      "SELECT",
      "OPTION",
      "SVG",
      "CANVAS",
    ].includes(tag)
  ) {
    return false;
  }
  if (parent.isContentEditable) return false;
  if (parent.closest("[contenteditable='true']")) return false;
  return !!node.nodeValue && !!node.nodeValue.trim();
}

function esVisible(el) {
  if (!el || el.closest("[hidden], [aria-hidden='true']")) return false;
  const style = window.getComputedStyle ? window.getComputedStyle(el) : null;
  if (style && (style.display === "none" || style.visibility === "hidden")) {
    return false;
  }
  if (typeof el.getClientRects === "function" && el.getClientRects().length === 0) {
    return false;
  }
  return true;
}

function normalizarTextoParaApi(texto) {
  return String(texto || "")
    .replace(/\s+/g, " ")
    .trim()
    .slice(0, MAX_ML_CHARS);
}

function crearMlId() {
  return "ml_" + Date.now().toString(36) + "_" + Math.random().toString(36).slice(2, 8);
}

function procesarNodoTexto(textNode) {
  const valor = textNode.nodeValue;
  regexActiva.lastIndex = 0;
  const matches = [...valor.matchAll(regexActiva)];
  if (matches.length === 0) return 0;

  const fragment = document.createDocumentFragment();
  let cursor = 0;

  for (const m of matches) {
    const start = m.index;
    const end = start + m[0].length;
    if (start > cursor) {
      fragment.appendChild(document.createTextNode(valor.slice(cursor, start)));
    }
    fragment.appendChild(crearMarcaLexicon(m[0]));
    cursor = end;
  }

  if (cursor < valor.length) {
    fragment.appendChild(document.createTextNode(valor.slice(cursor)));
  }

  const parent = textNode.parentNode;
  if (parent) {
    parent.replaceChild(fragment, textNode);
    if (parent.setAttribute) parent.setAttribute(HATE_NODE_FLAG, "1");
  }

  return matches.length;
}

function crearMarcaLexicon(textoOriginal) {
  return crearMarcaCensura({
    textoOriginal,
    origen: "lexicon",
    titulo: "Detectado por lexicon local",
  });
}

function crearMarcaML(textoOriginal, probabilidad, id, textoApi) {
  const p = Number.isFinite(probabilidad) ? probabilidad.toFixed(2) : "?";
  const mark = crearMarcaCensura({
    textoOriginal,
    origen: "ml",
    titulo: `BETO API: hate (p=${p})`,
  });
  mark.classList.add(ML_MARK_CLASS);
  mark.dataset.hateMlId = id;
  mark.dataset.hateMlProb = String(probabilidad);
  mark.addEventListener("click", (event) => {
    if (config.modo === "blur" || config.modo === "hide") return;
    event.stopPropagation();
    solicitarExplicacion(id, textoApi);
  });
  return mark;
}

function crearMarcaCensura({ textoOriginal, origen, titulo }) {
  const span = document.createElement("span");
  span.className = `${HATE_MARK_CLASS} hate-detect-mode-${config.modo}`;
  span.dataset.hateOriginal = textoOriginal;
  span.dataset.hateSource = origen;
  span.title = titulo;

  switch (config.modo) {
    case "asterisk":
      span.textContent = "*".repeat(Math.max(3, textoOriginal.trim().length || 3));
      span.title = titulo;
      break;
    case "blur":
      span.textContent = textoOriginal;
      span.title = `${titulo}. Clic para revelar`;
      span.addEventListener("click", () => span.classList.toggle("revealed"));
      break;
    case "hide":
      span.textContent = "[contenido oculto]";
      span.title = `${titulo}. Clic para revelar`;
      span.addEventListener("click", () => {
        span.textContent = textoOriginal;
        span.classList.add("revealed");
      });
      break;
    case "highlight":
    default:
      span.textContent = textoOriginal;
      break;
  }

  return span;
}

function enviarLoteAlModelo(fragmentos) {
  if (!config.apiHabilitada || !Array.isArray(fragmentos) || fragmentos.length === 0) {
    return;
  }

  const ids = fragmentos.map((f) => f.id);
  try {
    chrome.runtime.sendMessage({ tipo: "PREDICT_BATCH", fragmentos }, () => {
      if (chrome.runtime.lastError) {
        manejarApiNoDisponible({ ids, reason: "service_worker_unavailable" });
      }
    });
  } catch (_e) {
    manejarApiNoDisponible({ ids, reason: "send_message_failed" });
  }
}

function aplicarResultadoML(resultado) {
  const entry = window.__hateRefs && window.__hateRefs[resultado.id];
  if (!entry) return;

  config.apiDisponible = true;
  config.apiFallbackHasta = 0;

  const probabilidad = Number(resultado.probabilidad);
  const umbral = typeof config.umbralMl === "number" ? config.umbralMl : 0.7;
  const debeMarcar = Number.isFinite(probabilidad)
    ? probabilidad >= umbral
    : resultado.etiqueta === "hate";

  if (!debeMarcar) {
    marcarMlComoRevisado(entry, "checked");
    delete window.__hateRefs[resultado.id];
    scheduleScan(120);
    return;
  }

  const node = entry.node;
  const parent = entry.parent;
  const textoOriginal =
    node && node.nodeValue !== null ? node.nodeValue : entry.original || entry.texto;
  const marca = crearMarcaML(textoOriginal, probabilidad, resultado.id, entry.texto);
  const pTexto = Number.isFinite(probabilidad) ? probabilidad.toFixed(2) : "?";

  const refParent = conMutacionesPausadas(() => {
    if (node && node.parentNode && document.contains(node)) {
      node.parentNode.replaceChild(marca, node);
      if (parent && parent.setAttribute) {
        parent.setAttribute(ML_STATE_ATTR, "hit");
      }
      return marca;
    }
    if (parent && document.contains(parent)) {
      parent.classList.add("hate-ml");
      parent.setAttribute(ML_STATE_ATTR, "hit");
      parent.title = `BETO API: hate (p=${pTexto})`;
      return parent;
    }
    return marca;
  });

  window.__hateRefs[resultado.id] = {
    parent: refParent,
    texto: entry.texto,
    original: textoOriginal,
  };
  purgarRefsMl();

  config.detectados += 1;
  enviarStats();
  scheduleScan(120);
}

/*
 * Las referencias de detecciones confirmadas se conservan para poder pedir
 * la explicacion XAI al hacer clic. En paginas de scroll infinito eso
 * retendria nodos indefinidamente, asi que se descartan las mas antiguas
 * y las que ya no estan en el documento.
 */
function purgarRefsMl() {
  const ids = Object.keys(window.__hateRefs);
  if (ids.length <= MAX_REFS_ML) return;

  for (const id of ids) {
    const ref = window.__hateRefs[id];
    if (!ref || !ref.parent || !document.contains(ref.parent)) {
      delete window.__hateRefs[id];
    }
  }

  // Las pendientes esperan respuesta de la API; descartarlas dejaria su nodo
  // marcado como "pending" para siempre. Solo se evictan las ya resueltas.
  const evictables = Object.keys(window.__hateRefs).filter(
    (id) => !window.__hateRefs[id].node
  );
  const sobrantes = Object.keys(window.__hateRefs).length - MAX_REFS_ML;
  for (let i = 0; i < sobrantes && i < evictables.length; i += 1) {
    delete window.__hateRefs[evictables[i]];
  }
}

function marcarMlComoRevisado(entry, state) {
  if (entry && entry.parent && document.contains(entry.parent)) {
    entry.parent.setAttribute(ML_STATE_ATTR, state);
    entry.parent.removeAttribute(ML_ID_ATTR);
  }
}

function manejarEstadoApi(msg) {
  const estabaCaida = config.apiDisponible === false;
  config.apiDisponible = !!msg.ok;

  if (msg.ok) {
    config.apiFallbackHasta = 0;
    clearTimeout(apiRetryTimer);
    if (estabaCaida && config.activo && config.apiHabilitada) {
      reiniciarEscaneoCompleto();
      scheduleScan(0);
    }
  }
}

function manejarApiNoDisponible(msg = {}) {
  const ids = Array.isArray(msg.ids) ? msg.ids : [];
  config.apiDisponible = false;
  config.apiFallbackHasta = Date.now() + API_RETRY_MS;

  liberarPendientesMl(ids);

  if (config.activo) {
    scheduleScan(0);
    programarReintentoApi();
  }
}

function liberarPendientesMl(ids) {
  if (ids.length === 0) {
    Object.keys(window.__hateRefs).forEach((id) => {
      const ref = window.__hateRefs[id];
      if (!ref || !ref.parent || ref.parent.getAttribute?.(ML_STATE_ATTR) === "pending") {
        delete window.__hateRefs[id];
      }
    });
    document.querySelectorAll(`[${ML_STATE_ATTR}="pending"]`).forEach((el) => {
      el.removeAttribute(ML_STATE_ATTR);
      el.removeAttribute(ML_ID_ATTR);
    });
    return;
  }

  ids.forEach((id) => {
    const ref = window.__hateRefs[id];
    if (ref && ref.parent && document.contains(ref.parent)) {
      ref.parent.removeAttribute(ML_STATE_ATTR);
      ref.parent.removeAttribute(ML_ID_ATTR);
    }
    delete window.__hateRefs[id];
  });
}

function programarReintentoApi() {
  clearTimeout(apiRetryTimer);
  if (!config.apiHabilitada || !config.activo) return;

  apiRetryTimer = setTimeout(() => {
    if (!config.apiHabilitada || !config.activo) return;
    chrome.runtime.sendMessage({ tipo: "PING_API", url: config.apiUrl }, (res) => {
      if (chrome.runtime.lastError || !res || !res.ok) {
        config.apiDisponible = false;
        config.apiFallbackHasta = Date.now() + API_RETRY_MS;
        programarReintentoApi();
        return;
      }

      config.apiDisponible = true;
      config.apiFallbackHasta = 0;
      reiniciarEscaneoCompleto();
      scheduleScan(0);
    });
  }, API_RETRY_MS);
}

function solicitarExplicacion(id, texto) {
  if (!config.apiHabilitada || !texto) return;
  try {
    chrome.runtime.sendMessage({ tipo: "EXPLAIN_REQ", id, texto });
  } catch (_e) {
    /* La explicacion no bloquea la censura principal. */
  }
}

function aplicarExplicacion(resultado) {
  if (!resultado || !Array.isArray(resultado.tokens) || !Array.isArray(resultado.pesos)) {
    return;
  }

  const ref = window.__hateRefs && window.__hateRefs[resultado.id];
  const el = ref?.parent || buscarMlMark(resultado.id);
  if (!el || !document.contains(el)) return;

  const original = el.dataset.hateOriginal || el.textContent || "";
  const tokens = resultado.tokens
    .map((token, i) => ({
      token: limpiarTokenExplain(token),
      peso: Number(resultado.pesos[i] || 0),
    }))
    .filter((x) => x.token.length >= 2)
    .sort((a, b) => Math.abs(b.peso) - Math.abs(a.peso))
    .slice(0, 8);

  if (tokens.length === 0 || config.modo !== "highlight") {
    el.title = `${el.title || ""} | XAI: ${tokens
      .map((x) => `${x.token}:${x.peso.toFixed(2)}`)
      .join(", ")}`.trim();
    return;
  }

  const fragment = document.createDocumentFragment();
  let cursor = 0;
  const lower = original.toLowerCase();

  tokens.forEach(({ token, peso }) => {
    const idx = lower.indexOf(token.toLowerCase(), cursor);
    if (idx < 0) return;
    if (idx > cursor) fragment.appendChild(document.createTextNode(original.slice(cursor, idx)));
    const span = document.createElement("span");
    span.className = "hate-explain-token";
    span.toggleAttribute(peso >= 0 ? "data-shap-positive" : "data-shap-negative", true);
    span.textContent = original.slice(idx, idx + token.length);
    fragment.appendChild(span);
    cursor = idx + token.length;
  });

  if (cursor < original.length) {
    fragment.appendChild(document.createTextNode(original.slice(cursor)));
  }

  if (fragment.childNodes.length > 0) {
    conMutacionesPausadas(() => el.replaceChildren(fragment));
  }
}

function limpiarTokenExplain(token) {
  return String(token || "")
    .replace(/^#+/, "")
    .replace(/^##/, "")
    .replace(/[^\p{L}\p{N}_-]+/gu, "")
    .trim();
}

function buscarMlMark(id) {
  if (!id) return null;
  const safeId =
    typeof CSS !== "undefined" && typeof CSS.escape === "function"
      ? CSS.escape(id)
      : String(id).replace(/"/g, '\\"');
  return document.querySelector(`[data-hate-ml-id="${safeId}"]`);
}

function reiniciarEscaneoCompleto() {
  limpiarMarcas();
  limpiarEstadoMl();
  config.detectados = 0;
  enviarStats();
}

function limpiarMarcas() {
  conMutacionesPausadas(() => {
    document.querySelectorAll(`.${HATE_MARK_CLASS}`).forEach((mark) => {
      const original = mark.dataset.hateOriginal || mark.textContent || "";
      mark.replaceWith(document.createTextNode(original));
    });

    document.querySelectorAll(`[${HATE_NODE_FLAG}]`).forEach((el) => {
      el.removeAttribute(HATE_NODE_FLAG);
    });

    if (document.body && typeof document.body.normalize === "function") {
      document.body.normalize();
    }
  });
}

function limpiarEstadoMl() {
  document.querySelectorAll(`[${ML_STATE_ATTR}], [${ML_ID_ATTR}], .hate-ml`).forEach((el) => {
    el.removeAttribute(ML_STATE_ATTR);
    el.removeAttribute(ML_ID_ATTR);
    el.classList.remove("hate-ml");
  });
  window.__hateRefs = {};
}

function enviarStats() {
  try {
    chrome.runtime.sendMessage({
      tipo: "STATS_UPDATE",
      detectados: config.detectados,
      url: location.href,
      ruta: rutaActiva(),
    });
  } catch (_e) {
    /* El service worker puede estar dormido. */
  }
}
