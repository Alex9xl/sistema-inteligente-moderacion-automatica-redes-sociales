/**
 * api.js - Contrato HTTP con el backend BETO ajustado.
 *
 * La extension usa esta API como motor principal. Si /health indica que el
 * modelo no esta cargado o si /predict falla, el content script degrada al
 * lexicon local de respaldo.
 */

(function (root) {
  const DEFAULT_BASE_URL = "http://127.0.0.1:8000";
  const DEFAULT_TIMEOUT_MS = 4000;
  const CACHE_TTL_MS = 5 * 60 * 1000;
  const COLA_MAX = 3;

  const cache = new Map();
  const cola = [];
  let enVuelo = 0;
  let pausadoHasta = 0;
  let fallosConsecutivos = 0;
  let retryTimer = null;

  function normalizeBaseUrl(baseUrl = DEFAULT_BASE_URL) {
    return String(baseUrl || DEFAULT_BASE_URL).trim().replace(/\/+$/, "");
  }

  function cacheGet(key) {
    const entry = cache.get(key);
    if (!entry) return null;
    if (Date.now() - entry.t > CACHE_TTL_MS) {
      cache.delete(key);
      return null;
    }
    return entry.v;
  }

  function cacheSet(key, value) {
    cache.set(key, { t: Date.now(), v: value });
  }

  async function fetchConTimeout(url, options = {}, timeoutMs = DEFAULT_TIMEOUT_MS) {
    const ctrl = new AbortController();
    const timer = setTimeout(() => ctrl.abort(), timeoutMs);
    try {
      return await fetch(url, { ...options, signal: ctrl.signal });
    } finally {
      clearTimeout(timer);
    }
  }

  async function apiHealth(baseUrl = DEFAULT_BASE_URL, timeoutMs = 1500) {
    const cleanBaseUrl = normalizeBaseUrl(baseUrl);
    try {
      const r = await fetchConTimeout(cleanBaseUrl + "/health", {}, timeoutMs);
      if (!r.ok) return { status: "down", http: r.status };
      return await r.json();
    } catch (e) {
      return { status: "down", error: String(e) };
    }
  }

  async function apiPredict(texto, opts = {}) {
    const baseUrl = normalizeBaseUrl(opts.baseUrl || DEFAULT_BASE_URL);
    const cacheKey = "p:" + baseUrl + ":" + texto;
    const cached = cacheGet(cacheKey);
    if (cached) return cached;

    const r = await fetchConTimeout(
      baseUrl + "/predict",
      {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ texto }),
      },
      opts.timeoutMs || DEFAULT_TIMEOUT_MS
    );

    if (!r.ok) throw new Error("predict failed: HTTP " + r.status);
    const data = await r.json();
    cacheSet(cacheKey, data);
    return data;
  }

  async function apiExplain(texto, opts = {}) {
    const baseUrl = normalizeBaseUrl(opts.baseUrl || DEFAULT_BASE_URL);
    const r = await fetchConTimeout(
      baseUrl + "/explain",
      {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ texto }),
      },
      opts.timeoutMs || 8000
    );

    if (!r.ok) throw new Error("explain failed: HTTP " + r.status);
    return await r.json();
  }

  function enqueuePredict(item, onResult) {
    cola.push({ ...item, onResult });
    procesarCola();
  }

  async function procesarCola() {
    if (Date.now() < pausadoHasta) {
      programarReintentoCola();
      return;
    }

    while (cola.length && enVuelo < COLA_MAX) {
      const item = cola.shift();
      enVuelo += 1;
      apiPredict(item.texto, { baseUrl: item.baseUrl })
        .then((data) => {
          fallosConsecutivos = 0;
          item.onResult && item.onResult(null, { id: item.id, ...data });
        })
        .catch((err) => {
          fallosConsecutivos += 1;
          item.onResult && item.onResult(err);
          if (fallosConsecutivos >= 3) {
            pausadoHasta = Date.now() + 30000;
            programarReintentoCola();
          }
        })
        .finally(() => {
          enVuelo -= 1;
          procesarCola();
        });
    }
  }

  function programarReintentoCola() {
    clearTimeout(retryTimer);
    const delay = Math.max(0, pausadoHasta - Date.now());
    retryTimer = setTimeout(() => {
      retryTimer = null;
      procesarCola();
    }, delay);
  }

  root.HateApi = {
    DEFAULT_BASE_URL,
    normalizeBaseUrl,
    apiHealth,
    apiPredict,
    apiExplain,
    enqueuePredict,
    _cache: cache,
    _queue: cola,
  };
})(typeof self !== "undefined" ? self : globalThis);
