/**
 * Content Script - Beta del Detector ES
 *
 * Modo prototipo: detección 100% local con lexicón. La integración con
 * BETO via API local quedará habilitada cuando el endpoint /predict esté
 * disponible (ver `apiHabilitada`).
 *
 * Responsabilidades:
 *   - Escanear el DOM en busca de palabras del lexicón.
 *   - Aplicar el modo de censura configurado (highlight/blur/asterisk/hide).
 *   - Reaccionar a cambios del DOM con MutationObserver + debounce.
 *   - Reportar conteo de detecciones al service worker.
 *   - Limpiar todo cuando el usuario desactiva la detección.
 *
 * ──────────────────────────────────────────────────────────────────────
 * INTEGRACIÓN FUTURA CON BETO  (ver guia.md §15.5 / §15.6)
 * ──────────────────────────────────────────────────────────────────────
 *  Cuando el modelo BETO ajustado esté entrenado:
 *    1) Activar `apiHabilitada` desde la página de opciones.
 *    2) Llamar a `enviarLoteAlModelo(fragmentos)` después de cada escaneo.
 *    3) Implementar `aplicarResultadoML({id, etiqueta, probabilidad})`
 *       para envolver el nodo en una marca extra (.hate-ml) cuando la
 *       probabilidad supere `umbralMl`.
 *  Ya hay stubs señalizados con la etiqueta "TODO BETO".
 *  El módulo HateApi (api.js) ya está cargado y disponible como
 *  `self.HateApi` por si se prefiere llamar directamente a /predict
 *  desde el content script en lugar de pasarlo al service worker.
 * ──────────────────────────────────────────────────────────────────────
 */

const SCAN_DEBOUNCE_MS = 400;
const MAX_NODOS_POR_ESCANEO = 1500;
const HATE_MARK_CLASS = "hate-detect-mark";
const HATE_NODE_FLAG = "data-hate-scanned";

const config = {
  activo: false,
  modo: "highlight", // highlight | blur | asterisk | hide
  palabrasUsuarioActivas: true,
  apiHabilitada: false,
  apiUrl: "http://127.0.0.1:8000",
  lexiconUsuario: [],
  lexiconActivo: true,
  detectados: 0,
};

let regexActiva = null;
let observer = null;
let debounceTimer = null;

/* ============================================================
 * Inicialización
 * ============================================================ */

(async function init() {
  const stored = await chrome.storage.local.get([
    "deteccionActiva",
    "modoCensura",
    "palabrasUsuario",
    "lexiconActivo",
    "apiHabilitada",
  ]);

  config.activo = !!stored.deteccionActiva;
  config.modo = stored.modoCensura || "highlight";
  config.lexiconUsuario = Array.isArray(stored.palabrasUsuario)
    ? stored.palabrasUsuario
    : [];
  config.lexiconActivo = stored.lexiconActivo !== false;
  config.apiHabilitada = !!stored.apiHabilitada;

  rebuildRegex();

  if (config.activo) {
    activar();
  }
})();

/* ============================================================
 * Reaccionar a cambios de configuración
 * ============================================================ */

chrome.storage.onChanged.addListener((changes) => {
  let needRescan = false;
  let needRebuild = false;

  if (changes.deteccionActiva) {
    config.activo = !!changes.deteccionActiva.newValue;
    if (config.activo) {
      activar();
    } else {
      desactivar();
    }
  }
  if (changes.modoCensura) {
    config.modo = changes.modoCensura.newValue || "highlight";
    needRescan = true;
  }
  if (changes.palabrasUsuario) {
    config.lexiconUsuario = changes.palabrasUsuario.newValue || [];
    needRebuild = true;
  }
  if (changes.lexiconActivo) {
    config.lexiconActivo = changes.lexiconActivo.newValue !== false;
    needRebuild = true;
  }
  if (changes.apiHabilitada) {
    config.apiHabilitada = !!changes.apiHabilitada.newValue;
  }

  if (needRebuild) rebuildRegex();
  if ((needRescan || needRebuild) && config.activo) {
    limpiarMarcas();
    scheduleScan(0);
  }
});

/* ============================================================
 * Mensajes desde popup / background
 * ============================================================ */

chrome.runtime.onMessage.addListener((msg, _sender, sendResponse) => {
  if (msg && msg.tipo === "GET_STATS") {
    sendResponse({ detectados: config.detectados, activo: config.activo });
    return true;
  }
  if (msg && msg.tipo === "RESCAN") {
    if (config.activo) {
      limpiarMarcas();
      scheduleScan(0);
    }
    sendResponse({ ok: true });
    return true;
  }
  /* TODO BETO: cuando el backend esté listo, manejar:
   *   - msg.tipo === "RESULTADO"   -> aplicarResultadoML(msg)
   *   - msg.tipo === "EXPLAIN_RES" -> mostrar tooltip con tokens/pesos
   * (ver `aplicarResultadoML` y `enviarLoteAlModelo` más abajo).
   */
});

/* ============================================================
 * Activar / desactivar
 * ============================================================ */

function activar() {
  if (!observer) {
    observer = new MutationObserver(() => scheduleScan());
    observer.observe(document.body, { childList: true, subtree: true });
  }
  scheduleScan(0);
}

function desactivar() {
  if (observer) {
    observer.disconnect();
    observer = null;
  }
  limpiarMarcas();
  config.detectados = 0;
  enviarStats();
}

function scheduleScan(delay = SCAN_DEBOUNCE_MS) {
  if (!config.activo) return;
  if (debounceTimer) clearTimeout(debounceTimer);
  debounceTimer = setTimeout(escanear, delay);
}

/* ============================================================
 * Lexicón -> RegExp activa
 * ============================================================ */

function rebuildRegex() {
  const lista = [];
  if (config.lexiconActivo) {
    lista.push(...self.lexiconBuildDefaultSet());
  }
  if (Array.isArray(config.lexiconUsuario)) {
    lista.push(...config.lexiconUsuario);
  }
  // Dedup
  const unicos = Array.from(
    new Set(
      lista
        .filter((t) => typeof t === "string")
        .map((t) => t.toLowerCase().trim())
        .filter((t) => t.length > 0)
    )
  );
  regexActiva = self.lexiconBuildRegex(unicos);
}

/* ============================================================
 * Escaneo del DOM
 * ============================================================ */

function escanear() {
  if (!config.activo || !regexActiva) return;

  let nuevasDetecciones = 0;
  const walker = document.createTreeWalker(
    document.body,
    NodeFilter.SHOW_TEXT,
    {
      acceptNode(node) {
        const parent = node.parentElement;
        if (!parent) return NodeFilter.FILTER_REJECT;
        // Excluir scripts, estilos y campos editables
        const tag = parent.tagName;
        if (
          tag === "SCRIPT" ||
          tag === "STYLE" ||
          tag === "NOSCRIPT" ||
          tag === "TEXTAREA" ||
          tag === "INPUT"
        ) {
          return NodeFilter.FILTER_REJECT;
        }
        if (parent.isContentEditable) return NodeFilter.FILTER_REJECT;
        if (parent.closest(`.${HATE_MARK_CLASS}`)) return NodeFilter.FILTER_REJECT;
        if (parent.hasAttribute(HATE_NODE_FLAG)) return NodeFilter.FILTER_REJECT;
        if (!node.nodeValue || !node.nodeValue.trim()) return NodeFilter.FILTER_REJECT;
        return NodeFilter.FILTER_ACCEPT;
      },
    }
  );

  const objetivos = [];
  let visitados = 0;
  let n;
  while ((n = walker.nextNode())) {
    visitados++;
    if (visitados > MAX_NODOS_POR_ESCANEO) break;
    if (regexActiva.test(n.nodeValue)) {
      regexActiva.lastIndex = 0;
      objetivos.push(n);
    }
  }

  for (const textNode of objetivos) {
    const procesados = procesarNodoTexto(textNode);
    nuevasDetecciones += procesados;
  }

  if (nuevasDetecciones > 0) {
    config.detectados += nuevasDetecciones;
    enviarStats();
  }
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
    fragment.appendChild(crearMarca(m[0]));
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

function crearMarca(textoOriginal) {
  const span = document.createElement("span");
  span.className = HATE_MARK_CLASS + " hate-detect-mode-" + config.modo;
  span.dataset.hateOriginal = textoOriginal;

  switch (config.modo) {
    case "asterisk":
      span.textContent = "*".repeat(Math.max(3, textoOriginal.length));
      span.title = "Censurado por el detector";
      break;
    case "blur":
      span.textContent = textoOriginal;
      span.title = "Texto sospechoso (clic para revelar)";
      span.addEventListener("click", () => span.classList.toggle("revealed"));
      break;
    case "hide":
      span.textContent = "[contenido oculto]";
      span.title = "Texto oculto por el detector";
      span.addEventListener("click", () => {
        span.textContent = textoOriginal;
        span.classList.add("revealed");
      });
      break;
    case "highlight":
    default:
      span.textContent = textoOriginal;
      span.title = "Detectado: " + textoOriginal;
      break;
  }
  return span;
}

/* ============================================================
 * Limpieza
 * ============================================================ */

function limpiarMarcas() {
  const marcas = document.querySelectorAll("." + HATE_MARK_CLASS);
  marcas.forEach((mark) => {
    const original = mark.dataset.hateOriginal || mark.textContent || "";
    mark.replaceWith(document.createTextNode(original));
  });
  document.querySelectorAll(`[${HATE_NODE_FLAG}]`).forEach((el) => {
    el.removeAttribute(HATE_NODE_FLAG);
  });
  config.detectados = 0;
}

/* ============================================================
 * TODO BETO  ·  Stubs de integración con el modelo
 * ============================================================
 * Estas funciones quedan listas pero NO se invocan en la beta.
 * Para activarlas:
 *   1) En `escanear()`, después de marcar coincidencias del lexicón,
 *      acumular los textos de los nodos visibles en un arreglo
 *      { id, texto } y llamar `enviarLoteAlModelo(...)`.
 *   2) Implementar `aplicarResultadoML(...)` para envolver el nodo
 *      en un `<mark class="hate-ml">` cuando probabilidad >= umbralMl.
 *   3) Añadir las clases CSS .hate-ml y .hate-explain-token a styles.css
 *      (ver guia.md §15.10).
 */

// eslint-disable-next-line no-unused-vars
function enviarLoteAlModelo(fragmentos) {
  if (!config.apiHabilitada || !Array.isArray(fragmentos) || !fragmentos.length) return;
  try {
    chrome.runtime.sendMessage({ tipo: "PREDICT_BATCH", fragmentos });
  } catch (_e) { /* sw dormido */ }
}

// eslint-disable-next-line no-unused-vars
function aplicarResultadoML(_resultado) {
  // TODO BETO: localizar el nodo por id (window.__hateRefs[_resultado.id])
  //           y, si _resultado.probabilidad >= umbralMl, envolverlo en
  //           <mark class="hate-ml" title="p=...">.
}

/* ============================================================
 * Reporte de estadísticas
 * ============================================================ */

function enviarStats() {
  try {
    chrome.runtime.sendMessage({
      tipo: "STATS_UPDATE",
      detectados: config.detectados,
      url: location.href,
    });
  } catch (_e) {
    // ignorar si el service worker no está activo
  }
}
