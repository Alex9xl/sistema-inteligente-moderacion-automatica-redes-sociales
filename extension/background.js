/**
 * Service Worker (Manifest V3)
 *
 * Funciones del prototipo (beta):
 *   - Inicializar valores por defecto en chrome.storage al instalar.
 *   - Mantener un contador global y por pestaña de detecciones.
 *   - Actualizar el badge de la action con el conteo.
 *   - Refrescar el badge cuando el usuario activa/desactiva la detección.
 *   - Hacer ping al backend (PING_API) usando HateApi de api.js.
 *
 * ──────────────────────────────────────────────────────────────────────
 * INTEGRACIÓN CON BETO (cuando el modelo ajustado esté disponible)
 * ──────────────────────────────────────────────────────────────────────
 *  1. Levantar backend FastAPI (ver INSTRUCCIONES_PROYECTO.md §14):
 *       uvicorn src.api.main:app --host 127.0.0.1 --port 8000 --reload
 *  2. Activar `apiHabilitada=true` desde la página de opciones.
 *  3. Implementar el handler `PREDICT_BATCH` (ver TODO BETO más abajo) que
 *     llama a `HateApi.enqueuePredict` y reenvía el resultado al content
 *     script con el mensaje `RESULTADO`.
 *  4. (Opcional) Implementar el handler `EXPLAIN_REQ` -> `EXPLAIN_RES`
 *     para tooltips con SHAP.
 *
 * El contrato HTTP (predict/explain/health) ya está implementado en
 * `api.js` y validado contra INSTRUCCIONES_PROYECTO.md §14.4 / §15.9.
 * ──────────────────────────────────────────────────────────────────────
 */

// Cargar el módulo HateApi en el service worker.
try {
  importScripts("api.js");
} catch (e) {
  console.error("[Detector ES] No se pudo cargar api.js:", e);
}

const DEFAULTS = {
  deteccionActiva: false,
  modoCensura: "highlight", // highlight | blur | asterisk | hide
  umbralMl: 0.7,
  apiHabilitada: false,
  apiUrl: "http://127.0.0.1:8000",
  lexiconActivo: true,
  palabrasUsuario: [],
  estadisticas: { totalDetectados: 0, ultimaActualizacion: 0 },
};

const detectadosPorTab = {};

chrome.runtime.onInstalled.addListener(async () => {
  const stored = await chrome.storage.local.get(Object.keys(DEFAULTS));
  const updates = {};
  for (const [k, v] of Object.entries(DEFAULTS)) {
    if (stored[k] === undefined) updates[k] = v;
  }
  if (Object.keys(updates).length > 0) {
    await chrome.storage.local.set(updates);
  }
  await refrescarBadgeGlobal();
});

chrome.runtime.onStartup.addListener(refrescarBadgeGlobal);

/* Mensajes desde content scripts y popup ------------------------- */

chrome.runtime.onMessage.addListener((msg, sender, sendResponse) => {
  if (!msg || !msg.tipo) return;

  switch (msg.tipo) {
    case "STATS_UPDATE":
      handleStatsUpdate(msg, sender);
      sendResponse({ ok: true });
      break;

    case "RESET_STATS":
      Object.keys(detectadosPorTab).forEach((k) => delete detectadosPorTab[k]);
      chrome.storage.local.set({
        estadisticas: { totalDetectados: 0, ultimaActualizacion: Date.now() },
      });
      refrescarBadgeGlobal();
      sendResponse({ ok: true });
      break;

    case "GET_GLOBAL_STATS":
      chrome.storage.local.get(["estadisticas"], (s) => {
        sendResponse(s.estadisticas || DEFAULTS.estadisticas);
      });
      return true; // async

    case "PING_API":
      pingApi(msg.url || DEFAULTS.apiUrl).then(sendResponse);
      return true; // async

    /* ─────────────────────────────────────────────────────────────
     * TODO BETO  ·  Cuando apiHabilitada=true y el backend esté listo,
     * el content script enviará lotes de fragmentos a inferir aquí.
     * Ver INSTRUCCIONES_PROYECTO.md §15.4 / §15.6.
     * ───────────────────────────────────────────────────────────── */
    case "PREDICT_BATCH":
      handlePredictBatch(msg, sender);
      sendResponse({ ok: true });
      break;

    case "EXPLAIN_REQ":
      handleExplainReq(msg, sender);
      sendResponse({ ok: true });
      break;
  }
});

/* ============================================================
 * TODO BETO · Handlers de inferencia (placeholders)
 * ============================================================
 * Estas funciones quedan listas para activar cuando el modelo BETO
 * ajustado esté entrenado y el backend FastAPI esté corriendo.
 * Mientras `apiHabilitada=false`, no hacen nada y la detección
 * funciona 100% por lexicón local.
 */

async function handlePredictBatch(msg, sender) {
  const { apiHabilitada, apiUrl } = await chrome.storage.local.get([
    "apiHabilitada",
    "apiUrl",
  ]);
  if (!apiHabilitada || !self.HateApi) return;
  const tabId = sender?.tab?.id;
  if (typeof tabId !== "number" || !Array.isArray(msg.fragmentos)) return;

  for (const f of msg.fragmentos) {
    self.HateApi.enqueuePredict(
      { id: f.id, texto: f.texto, baseUrl: apiUrl || DEFAULTS.apiUrl },
      (err, data) => {
        if (err) {
          // Backend caído: badge rojo y dejar de encolar (api.js ya hace backoff).
          chrome.action.setBadgeText({ text: "!", tabId });
          chrome.action.setBadgeBackgroundColor({ color: "#c00", tabId });
          return;
        }
        try {
          chrome.tabs.sendMessage(tabId, {
            tipo: "RESULTADO",
            id: data.id,
            etiqueta: data.etiqueta,
            probabilidad: data.probabilidad,
          });
        } catch (_e) { /* tab cerrada */ }
      }
    );
  }
}

async function handleExplainReq(msg, sender) {
  const { apiHabilitada, apiUrl } = await chrome.storage.local.get([
    "apiHabilitada",
    "apiUrl",
  ]);
  if (!apiHabilitada || !self.HateApi) return;
  const tabId = sender?.tab?.id;
  if (typeof tabId !== "number" || !msg.texto) return;
  try {
    const data = await self.HateApi.apiExplain(msg.texto, {
      baseUrl: apiUrl || DEFAULTS.apiUrl,
    });
    chrome.tabs.sendMessage(tabId, {
      tipo: "EXPLAIN_RES",
      id: msg.id,
      tokens: data.tokens,
      pesos: data.pesos,
    });
  } catch (_e) { /* fallar silenciosamente en beta */ }
}

async function handleStatsUpdate(msg, sender) {
  const tabId = sender?.tab?.id;
  if (typeof tabId === "number") {
    detectadosPorTab[tabId] = msg.detectados || 0;
    actualizarBadgeTab(tabId, msg.detectados || 0);
  }

  // Acumular totales globales
  const stored = await chrome.storage.local.get(["estadisticas"]);
  const stats = stored.estadisticas || DEFAULTS.estadisticas;
  const totalActual = Object.values(detectadosPorTab).reduce((a, b) => a + b, 0);
  stats.totalDetectados = totalActual;
  stats.ultimaActualizacion = Date.now();
  await chrome.storage.local.set({ estadisticas: stats });
}

/* Cambios en storage -> badge ----------------------------------- */

chrome.storage.onChanged.addListener((changes) => {
  if (changes.deteccionActiva) {
    refrescarBadgeGlobal();
  }
});

/* Limpiar contador cuando una pestaña se cierra ----------------- */

chrome.tabs.onRemoved.addListener((tabId) => {
  delete detectadosPorTab[tabId];
});

/* Helpers de badge ---------------------------------------------- */

async function refrescarBadgeGlobal() {
  const { deteccionActiva } = await chrome.storage.local.get([
    "deteccionActiva",
  ]);
  if (deteccionActiva) {
    chrome.action.setBadgeBackgroundColor({ color: "#7c3aed" });
  } else {
    chrome.action.setBadgeText({ text: "" });
    chrome.action.setBadgeBackgroundColor({ color: "#6b7280" });
  }
}

function actualizarBadgeTab(tabId, n) {
  const text = n > 0 ? (n > 99 ? "99+" : String(n)) : "";
  try {
    chrome.action.setBadgeText({ text, tabId });
  } catch (_e) {
    chrome.action.setBadgeText({ text });
  }
}

/* Ping API (delegado a HateApi.apiHealth) ----------------------- */

async function pingApi(url) {
  if (!self.HateApi) {
    return { ok: false, error: "api.js no cargado" };
  }
  const data = await self.HateApi.apiHealth(url, 1500);
  if (data && data.status === "ok") return { ok: true, data };
  return { ok: false, data };
}
