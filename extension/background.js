/**
 * Service worker - Detector ES v1.0.
 *
 * Mantiene estado global, badge, ping de salud de la API y puente entre el
 * content script y el backend BETO local.
 */

try {
  importScripts("api.js");
} catch (e) {
  console.error("[Detector ES] No se pudo cargar api.js:", e);
}

const DEFAULTS = {
  deteccionActiva: false,
  modoCensura: "highlight",
  umbralMl: 0.7,
  apiHabilitada: true,
  apiUrl: "http://127.0.0.1:8000",
  lexiconActivo: true,
  palabrasUsuario: [],
  estadisticas: { totalDetectados: 0, ultimaActualizacion: 0 },
  configVersion: "1.0",
};

const API_HEALTH_TTL_MS = 10000;
const API_BACKOFF_MS = 30000;

const detectadosPorTab = {};
let apiHealthState = {
  baseUrl: "",
  ok: false,
  checkedAt: 0,
  backoffUntil: 0,
  data: null,
};

chrome.runtime.onInstalled.addListener(async () => {
  const stored = await chrome.storage.local.get(Object.keys(DEFAULTS));
  const updates = {};
  for (const [k, v] of Object.entries(DEFAULTS)) {
    if (stored[k] === undefined) updates[k] = v;
  }
  if (stored.configVersion !== "1.0") {
    updates.apiHabilitada = true;
    updates.configVersion = "1.0";
  }
  if (Object.keys(updates).length > 0) {
    await chrome.storage.local.set(updates);
  }
  await refrescarBadgeGlobal();
});

chrome.runtime.onStartup.addListener(refrescarBadgeGlobal);

chrome.runtime.onMessage.addListener((msg, sender, sendResponse) => {
  if (!msg || !msg.tipo) return false;

  switch (msg.tipo) {
    case "STATS_UPDATE":
      handleStatsUpdate(msg, sender);
      sendResponse({ ok: true });
      return true;

    case "RESET_STATS":
      Object.keys(detectadosPorTab).forEach((k) => delete detectadosPorTab[k]);
      chrome.storage.local.set({
        estadisticas: { totalDetectados: 0, ultimaActualizacion: Date.now() },
      });
      refrescarBadgeGlobal();
      sendResponse({ ok: true });
      return true;

    case "GET_GLOBAL_STATS":
      chrome.storage.local.get(["estadisticas"], (s) => {
        sendResponse(s.estadisticas || DEFAULTS.estadisticas);
      });
      return true;

    case "PING_API":
      pingApi(msg.url || DEFAULTS.apiUrl).then(sendResponse);
      return true;

    case "PREDICT_BATCH":
      handlePredictBatch(msg, sender).catch((err) => {
        const tabId = sender?.tab?.id;
        if (typeof tabId === "number") {
          notifyApiUnavailable(tabId, extraerIds(msg.fragmentos), {
            reason: "predict_batch_error",
            error: String(err),
          });
        }
      });
      sendResponse({ ok: true });
      return true;

    case "EXPLAIN_REQ":
      handleExplainReq(msg, sender).catch(() => {
        const tabId = sender?.tab?.id;
        if (typeof tabId === "number") {
          notifyApiStatus(tabId, false, { reason: "explain_failed" });
        }
      });
      sendResponse({ ok: true });
      return true;

    default:
      return false;
  }
});

async function handlePredictBatch(msg, sender) {
  const tabId = sender?.tab?.id;
  if (typeof tabId !== "number" || !Array.isArray(msg.fragmentos)) return;

  const fragmentos = msg.fragmentos
    .filter((f) => f && typeof f.id === "string" && typeof f.texto === "string")
    .filter((f) => f.texto.trim().length > 0);
  if (fragmentos.length === 0) return;

  const { apiHabilitada, apiUrl } = await chrome.storage.local.get([
    "apiHabilitada",
    "apiUrl",
  ]);

  if (apiHabilitada === false || !self.HateApi) {
    notifyApiUnavailable(tabId, extraerIds(fragmentos), { reason: "api_disabled" });
    return;
  }

  const baseUrl = apiUrl || DEFAULTS.apiUrl;
  const ready = await ensureApiReady(baseUrl);
  if (!ready.ok) {
    notifyApiUnavailable(tabId, extraerIds(fragmentos), ready);
    return;
  }

  notifyApiStatus(tabId, true, ready);

  const batchIds = extraerIds(fragmentos);
  let batchFailed = false;

  for (const f of fragmentos) {
    self.HateApi.enqueuePredict(
      { id: f.id, texto: f.texto, baseUrl },
      (err, data) => {
        if (err) {
          registrarApiFallida(baseUrl, err);
          mostrarBadgeError(tabId);
          if (!batchFailed) {
            batchFailed = true;
            notifyApiUnavailable(tabId, batchIds, {
              reason: "predict_failed",
              error: String(err),
            });
          }
          return;
        }

        if (batchFailed) return;

        notifyApiStatus(tabId, true, { data: apiHealthState.data });
        chrome.tabs.sendMessage(tabId, {
          tipo: "RESULTADO",
          id: data.id,
          etiqueta: data.etiqueta,
          probabilidad: data.probabilidad,
        });
      }
    );
  }
}

async function handleExplainReq(msg, sender) {
  const tabId = sender?.tab?.id;
  if (typeof tabId !== "number" || !msg.texto || !self.HateApi) return;

  const { apiHabilitada, apiUrl } = await chrome.storage.local.get([
    "apiHabilitada",
    "apiUrl",
  ]);
  if (apiHabilitada === false) return;

  const baseUrl = apiUrl || DEFAULTS.apiUrl;
  const ready = await ensureApiReady(baseUrl);
  if (!ready.ok) {
    notifyApiUnavailable(tabId, [msg.id], ready);
    return;
  }

  const data = await self.HateApi.apiExplain(msg.texto, { baseUrl });
  chrome.tabs.sendMessage(tabId, {
    tipo: "EXPLAIN_RES",
    id: msg.id,
    tokens: data.tokens,
    pesos: data.pesos,
  });
}

async function ensureApiReady(baseUrl) {
  const now = Date.now();
  if (apiHealthState.baseUrl === baseUrl && now < apiHealthState.backoffUntil) {
    return {
      ok: false,
      reason: "api_backoff",
      retryAfterMs: apiHealthState.backoffUntil - now,
      data: apiHealthState.data,
    };
  }

  if (
    apiHealthState.baseUrl === baseUrl &&
    apiHealthState.ok &&
    now - apiHealthState.checkedAt < API_HEALTH_TTL_MS
  ) {
    return { ok: true, data: apiHealthState.data };
  }

  const health = await pingApi(baseUrl);
  if (!health.ok) {
    apiHealthState.backoffUntil = Date.now() + API_BACKOFF_MS;
  }
  return health;
}

async function pingApi(url) {
  if (!self.HateApi) {
    return { ok: false, reason: "api_js_missing", error: "api.js no cargado" };
  }

  const baseUrl = self.HateApi.normalizeBaseUrl
    ? self.HateApi.normalizeBaseUrl(url)
    : url || DEFAULTS.apiUrl;
  const data = await self.HateApi.apiHealth(baseUrl, 1500);
  const statusOk = data && data.status === "ok";
  const modelReady = data && data.model_loaded !== false;
  const ok = Boolean(statusOk && modelReady);

  apiHealthState = {
    baseUrl,
    ok,
    checkedAt: Date.now(),
    backoffUntil: ok ? 0 : Date.now() + API_BACKOFF_MS,
    data,
  };

  if (ok) return { ok: true, data };
  if (statusOk && !modelReady) {
    return { ok: false, reason: "model_not_loaded", data };
  }
  return { ok: false, reason: "api_down", data };
}

function registrarApiFallida(baseUrl, err) {
  apiHealthState = {
    baseUrl,
    ok: false,
    checkedAt: Date.now(),
    backoffUntil: Date.now() + API_BACKOFF_MS,
    data: { error: String(err) },
  };
}

function notifyApiUnavailable(tabId, ids, detail = {}) {
  try {
    chrome.tabs.sendMessage(tabId, {
      tipo: "API_UNAVAILABLE",
      ids,
      ...detail,
    });
  } catch (_e) {
    /* Pestaña cerrada o sin content script. */
  }
}

function notifyApiStatus(tabId, ok, detail = {}) {
  try {
    chrome.tabs.sendMessage(tabId, {
      tipo: "API_STATUS",
      ok,
      ...detail,
    });
  } catch (_e) {
    /* Pestaña cerrada o sin content script. */
  }
}

function extraerIds(fragmentos) {
  return Array.isArray(fragmentos)
    ? fragmentos.filter((f) => f && typeof f.id === "string").map((f) => f.id)
    : [];
}

function mostrarBadgeError(tabId) {
  try {
    chrome.action.setBadgeText({ text: "!", tabId });
    chrome.action.setBadgeBackgroundColor({ color: "#dc2626", tabId });
  } catch (_e) {
    chrome.action.setBadgeText({ text: "!" });
    chrome.action.setBadgeBackgroundColor({ color: "#dc2626" });
  }
}

async function handleStatsUpdate(msg, sender) {
  const tabId = sender?.tab?.id;
  if (typeof tabId === "number") {
    detectadosPorTab[tabId] = msg.detectados || 0;
    actualizarBadgeTab(tabId, msg.detectados || 0);
  }

  const stored = await chrome.storage.local.get(["estadisticas"]);
  const stats = stored.estadisticas || DEFAULTS.estadisticas;
  const totalActual = Object.values(detectadosPorTab).reduce((a, b) => a + b, 0);
  stats.totalDetectados = totalActual;
  stats.ultimaActualizacion = Date.now();
  await chrome.storage.local.set({ estadisticas: stats });
}

chrome.storage.onChanged.addListener((changes) => {
  if (changes.deteccionActiva) {
    refrescarBadgeGlobal();
  }
  if (changes.apiUrl || changes.apiHabilitada) {
    apiHealthState = {
      baseUrl: "",
      ok: false,
      checkedAt: 0,
      backoffUntil: 0,
      data: null,
    };
  }
});

chrome.tabs.onRemoved.addListener((tabId) => {
  delete detectadosPorTab[tabId];
});

async function refrescarBadgeGlobal() {
  const { deteccionActiva } = await chrome.storage.local.get(["deteccionActiva"]);
  if (deteccionActiva) {
    chrome.action.setBadgeBackgroundColor({ color: "#2563eb" });
  } else {
    chrome.action.setBadgeText({ text: "" });
    chrome.action.setBadgeBackgroundColor({ color: "#6b7280" });
  }
}

function actualizarBadgeTab(tabId, n) {
  const text = n > 0 ? (n > 99 ? "99+" : String(n)) : "";
  try {
    chrome.action.setBadgeText({ text, tabId });
    chrome.action.setBadgeBackgroundColor({ color: "#2563eb", tabId });
  } catch (_e) {
    chrome.action.setBadgeText({ text });
    chrome.action.setBadgeBackgroundColor({ color: "#2563eb" });
  }
}
