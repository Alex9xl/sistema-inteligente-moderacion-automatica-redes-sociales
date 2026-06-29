/**
 * api.js  —  Contrato HTTP con el backend BETO ajustado.
 *
 * Estado actual: STUB FUNCIONAL (beta).
 * Mientras el modelo BETO ajustado de la tesis no esté disponible, esta capa
 * existe sólo para:
 *   1. Hacer "ping" al endpoint /health desde el popup y la página de opciones.
 *   2. Mantener listo el contrato y la cola de inferencia.
 *
 * Cuando el backend esté disponible (ver `src/api/main.py` y INSTRUCCIONES_PROYECTO.md §14):
 *   - apiPredict() y apiExplain() ya hablan el contrato correcto.
 *   - El service worker sólo tendrá que activar `apiHabilitada` y empezar
 *     a llamar a `enqueuePredict()` desde `procesarLoteContent()`.
 *
 * Endpoints (INSTRUCCIONES_PROYECTO.md §14.4):
 *   POST /predict   { texto: string }                  -> { etiqueta, probabilidad, modelo, version }
 *   POST /explain   { texto: string }                  -> { ..., tokens, pesos }
 *   GET  /health                                       -> { status, model_loaded, model_version }
 *
 * Este archivo se carga tanto en el content script como en el service worker.
 *   - En content script: se expone como `self.HateApi`.
 *   - En service worker: se carga vía `importScripts("api.js")`.
 */

(function (root) {
  const DEFAULT_BASE_URL = "http://127.0.0.1:8000";
  const DEFAULT_TIMEOUT_MS = 4000;

  /* ============================================================
   * Caché en memoria con TTL (ver INSTRUCCIONES_PROYECTO.md §15.11)
   * Evita repreguntar el mismo fragmento al backend en una sesión.
   * ============================================================ */

  const CACHE_TTL_MS = 5 * 60 * 1000;
  const cache = new Map();

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

  /* ============================================================
   * Helper de fetch con timeout
   * ============================================================ */

  async function fetchConTimeout(url, options = {}, timeoutMs = DEFAULT_TIMEOUT_MS) {
    const ctrl = new AbortController();
    const timer = setTimeout(() => ctrl.abort(), timeoutMs);
    try {
      const r = await fetch(url, { ...options, signal: ctrl.signal });
      return r;
    } finally {
      clearTimeout(timer);
    }
  }

  /* ============================================================
   * Endpoints
   * ============================================================ */

  /**
   * GET /health
   * @returns {Promise<{status: string, model_loaded?: boolean, model_version?: string}>}
   */
  async function apiHealth(baseUrl = DEFAULT_BASE_URL, timeoutMs = 1500) {
    try {
      const r = await fetchConTimeout(baseUrl + "/health", {}, timeoutMs);
      if (!r.ok) return { status: "down", http: r.status };
      return await r.json();
    } catch (e) {
      return { status: "down", error: String(e) };
    }
  }

  /**
   * POST /predict
   * @param {string} texto
   * @param {{baseUrl?: string, timeoutMs?: number}} opts
   * @returns {Promise<{etiqueta: "hate"|"no_hate", probabilidad: number, modelo: string, version: string}>}
   */
  async function apiPredict(texto, opts = {}) {
    const baseUrl = opts.baseUrl || DEFAULT_BASE_URL;
    const cacheKey = "p:" + texto;
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

  /**
   * POST /explain
   * @param {string} texto
   * @returns {Promise<{etiqueta: string, probabilidad: number, modelo: string, version: string, tokens: string[], pesos: number[]}>}
   */
  async function apiExplain(texto, opts = {}) {
    const baseUrl = opts.baseUrl || DEFAULT_BASE_URL;
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

  /* ============================================================
   * Cola con concurrencia limitada (INSTRUCCIONES_PROYECTO.md §15.6 / §15.11)
   * ============================================================ */

  const COLA_MAX = 3;
  const cola = [];
  let enVuelo = 0;
  let pausadoHasta = 0;
  let fallosConsecutivos = 0;

  /**
   * Encola una predicción. `onResult` se llama con el resultado o el error.
   * @param {{id: string, texto: string, baseUrl?: string}} item
   * @param {(err: Error|null, data?: any) => void} onResult
   */
  function enqueuePredict(item, onResult) {
    cola.push({ ...item, onResult });
    procesarCola();
  }

  async function procesarCola() {
    if (Date.now() < pausadoHasta) return;
    while (cola.length && enVuelo < COLA_MAX) {
      const item = cola.shift();
      enVuelo++;
      apiPredict(item.texto, { baseUrl: item.baseUrl })
        .then((data) => {
          fallosConsecutivos = 0;
          item.onResult && item.onResult(null, { id: item.id, ...data });
        })
        .catch((err) => {
          fallosConsecutivos++;
          item.onResult && item.onResult(err);
          // Backoff: 3 fallos seguidos -> 30 s sin enviar
          if (fallosConsecutivos >= 3) {
            pausadoHasta = Date.now() + 30000;
          }
        })
        .finally(() => {
          enVuelo--;
          procesarCola();
        });
    }
  }

  /* ============================================================
   * Exponer
   * ============================================================ */

  const HateApi = {
    DEFAULT_BASE_URL,
    apiHealth,
    apiPredict,
    apiExplain,
    enqueuePredict,
    _cache: cache, // útil para depurar
  };

  // En content scripts y service workers globalThis === self.
  root.HateApi = HateApi;
})(typeof self !== "undefined" ? self : globalThis);
