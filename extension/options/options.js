/**
 * Options page - lógica completa de configuración del lexicón personal.
 *
 * Funcionalidades:
 *   - Listar / agregar / quitar / borrar todos los términos
 *   - Buscar dentro de la lista personal
 *   - Importar y exportar JSON (respaldo local)
 *   - Restaurar lista por defecto (vacía la personal)
 *   - Cambiar modo de censura, activar/desactivar diccionario base
 *   - Configurar API BETO principal, umbral y URL del backend local
 */

const MAX_TERMINOS = 200;
const MAX_LEN = 64;

const els = {
  formAgregar: document.getElementById("formAgregar"),
  inputPalabra: document.getElementById("inputPalabra"),
  inputSearch: document.getElementById("inputSearch"),
  listaTerminos: document.getElementById("listaTerminos"),
  emptyState: document.getElementById("emptyState"),
  counterValue: document.getElementById("counterValue"),
  btnClearAll: document.getElementById("btnClearAll"),
  btnExport: document.getElementById("btnExport"),
  fileImport: document.getElementById("fileImport"),
  btnRestore: document.getElementById("btnRestore"),
  defaultCategories: document.getElementById("defaultCategories"),
  settingDeteccion: document.getElementById("settingDeteccion"),
  settingLexiconBase: document.getElementById("settingLexiconBase"),
  selectModo: document.getElementById("selectModo"),
  settingApi: document.getElementById("settingApi"),
  inputUmbral: document.getElementById("inputUmbral"),
  umbralValue: document.getElementById("umbralValue"),
  inputApiUrl: document.getElementById("inputApiUrl"),
  apiStatusDot: document.getElementById("apiStatusDot"),
  apiStatusText: document.getElementById("apiStatusText"),
  btnPingApi: document.getElementById("btnPingApi"),
  toast: document.getElementById("toast"),
};

let palabras = [];
let filtro = "";

document.addEventListener("DOMContentLoaded", init);

/* ============================================================
 * Inicialización
 * ============================================================ */

async function init() {
  const stored = await chrome.storage.local.get([
    "palabrasUsuario",
    "deteccionActiva",
    "lexiconActivo",
    "modoCensura",
    "apiHabilitada",
    "umbralMl",
    "apiUrl",
  ]);

  palabras = Array.isArray(stored.palabrasUsuario)
    ? stored.palabrasUsuario
    : [];
  els.settingDeteccion.checked = !!stored.deteccionActiva;
  els.settingLexiconBase.checked = stored.lexiconActivo !== false;
  els.selectModo.value = stored.modoCensura || "highlight";
  els.settingApi.checked = stored.apiHabilitada !== false;
  els.inputUmbral.value = stored.umbralMl ?? 0.7;
  els.umbralValue.textContent = Number(stored.umbralMl ?? 0.7).toFixed(2);
  els.inputApiUrl.value = stored.apiUrl || "http://127.0.0.1:8000";

  renderLista();
  renderCategorias();
  bindEventos();
  pingApi();
}

function bindEventos() {
  els.formAgregar.addEventListener("submit", (e) => {
    e.preventDefault();
    agregar(els.inputPalabra.value);
  });

  els.inputSearch.addEventListener("input", () => {
    filtro = els.inputSearch.value.trim().toLowerCase();
    renderLista();
  });

  els.btnClearAll.addEventListener("click", confirmBorrarTodo);
  els.btnExport.addEventListener("click", exportar);
  els.btnRestore.addEventListener("click", confirmRestaurar);
  els.fileImport.addEventListener("change", importar);

  els.settingDeteccion.addEventListener("change", () =>
    chrome.storage.local.set({ deteccionActiva: els.settingDeteccion.checked })
  );
  els.settingLexiconBase.addEventListener("change", () =>
    chrome.storage.local.set({ lexiconActivo: els.settingLexiconBase.checked })
  );
  els.selectModo.addEventListener("change", () =>
    chrome.storage.local.set({ modoCensura: els.selectModo.value })
  );
  els.settingApi.addEventListener("change", async () => {
    await chrome.storage.local.set({ apiHabilitada: els.settingApi.checked });
    pingApi();
  });
  els.inputUmbral.addEventListener("input", () => {
    const value = Number(els.inputUmbral.value);
    els.umbralValue.textContent = value.toFixed(2);
    chrome.storage.local.set({ umbralMl: value });
  });
  els.inputApiUrl.addEventListener("change", () => {
    const url = normalizarApiUrl(els.inputApiUrl.value);
    els.inputApiUrl.value = url;
    chrome.storage.local.set({ apiUrl: url });
    toast("URL del backend actualizada", "success");
    pingApi();
  });
  els.btnPingApi.addEventListener("click", pingApi);

  // Reaccionar a cambios externos
  chrome.storage.onChanged.addListener((changes) => {
    if (changes.palabrasUsuario) {
      palabras = changes.palabrasUsuario.newValue || [];
      renderLista();
    }
    if (changes.deteccionActiva)
      els.settingDeteccion.checked = !!changes.deteccionActiva.newValue;
    if (changes.lexiconActivo)
      els.settingLexiconBase.checked =
        changes.lexiconActivo.newValue !== false;
    if (changes.modoCensura)
      els.selectModo.value = changes.modoCensura.newValue || "highlight";
    if (changes.apiHabilitada)
      els.settingApi.checked = changes.apiHabilitada.newValue !== false;
    if (changes.umbralMl) {
      const value = Number(changes.umbralMl.newValue ?? 0.7);
      els.inputUmbral.value = value;
      els.umbralValue.textContent = value.toFixed(2);
    }
    if (changes.apiUrl) els.inputApiUrl.value = changes.apiUrl.newValue;
  });
}

/* ============================================================
 * Listado
 * ============================================================ */

function renderLista() {
  els.listaTerminos.innerHTML = "";
  els.counterValue.textContent = String(palabras.length);

  const filtradas = filtro
    ? palabras.filter((p) => p.toLowerCase().includes(filtro))
    : palabras;

  if (palabras.length === 0) {
    els.emptyState.classList.remove("hidden");
  } else {
    els.emptyState.classList.add("hidden");
  }

  if (filtradas.length === 0 && palabras.length > 0) {
    const li = document.createElement("li");
    li.style.cssText =
      "color:var(--text-muted);font-size:12px;list-style:none;padding:8px 4px;";
    li.textContent = `Sin coincidencias para "${filtro}"`;
    els.listaTerminos.appendChild(li);
    return;
  }

  for (const t of filtradas) {
    const li = document.createElement("li");
    li.className = "chip";
    const span = document.createElement("span");
    span.textContent = t;
    const btn = document.createElement("button");
    btn.type = "button";
    btn.title = `Quitar “${t}”`;
    btn.setAttribute("aria-label", `Quitar ${t}`);
    btn.textContent = "×";
    btn.addEventListener("click", () => quitar(t));
    li.appendChild(span);
    li.appendChild(btn);
    els.listaTerminos.appendChild(li);
  }
}

/* ============================================================
 * CRUD palabras
 * ============================================================ */

async function agregar(raw) {
  const t = (raw || "").trim().toLowerCase();
  if (!t) return;
  if (t.length > MAX_LEN) {
    toast(`Máximo ${MAX_LEN} caracteres por término`, "error");
    return;
  }
  if (palabras.includes(t)) {
    toast(`"${t}" ya está en tu lista`, "error");
    return;
  }
  if (palabras.length >= MAX_TERMINOS) {
    toast(`Límite de ${MAX_TERMINOS} términos alcanzado`, "error");
    return;
  }
  palabras = [...palabras, t];
  await persistir();
  els.inputPalabra.value = "";
  els.inputPalabra.focus();
  toast(`Agregado: ${t}`, "success");
}

async function quitar(t) {
  palabras = palabras.filter((p) => p !== t);
  await persistir();
  toast(`Quitado: ${t}`, "success");
}

async function confirmBorrarTodo() {
  if (palabras.length === 0) return;
  if (!confirm(`¿Borrar los ${palabras.length} términos de tu lista?`)) return;
  palabras = [];
  await persistir();
  toast("Lista personal borrada", "success");
}

async function confirmRestaurar() {
  if (
    !confirm(
      "Esto vaciará tu lista personal. El diccionario base se mantiene activo. ¿Continuar?"
    )
  )
    return;
  palabras = [];
  await chrome.storage.local.set({
    palabrasUsuario: palabras,
    lexiconActivo: true,
    modoCensura: "highlight",
  });
  els.settingLexiconBase.checked = true;
  els.selectModo.value = "highlight";
  toast("Configuración restaurada", "success");
}

async function persistir() {
  await chrome.storage.local.set({ palabrasUsuario: palabras });
  renderLista();
}

/* ============================================================
 * Exportar / Importar
 * ============================================================ */

function exportar() {
  const payload = {
    schema: "detector-es-lexicon-personal",
    version: 1,
    exportedAt: new Date().toISOString(),
    palabras,
  };
  const blob = new Blob([JSON.stringify(payload, null, 2)], {
    type: "application/json",
  });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = `lexicon-personal-${new Date()
    .toISOString()
    .slice(0, 10)}.json`;
  document.body.appendChild(a);
  a.click();
  a.remove();
  URL.revokeObjectURL(url);
  toast("Lexicón exportado", "success");
}

function importar(e) {
  const file = e.target.files?.[0];
  if (!file) return;
  const reader = new FileReader();
  reader.onload = async () => {
    try {
      const data = JSON.parse(reader.result);
      let arr = [];
      if (Array.isArray(data)) arr = data;
      else if (Array.isArray(data.palabras)) arr = data.palabras;
      else throw new Error("Formato no reconocido");

      const sane = arr
        .filter((x) => typeof x === "string")
        .map((x) => x.trim().toLowerCase())
        .filter((x) => x.length > 0 && x.length <= MAX_LEN);
      // Merge con existentes y dedup
      const set = new Set([...palabras, ...sane]);
      palabras = Array.from(set).slice(0, MAX_TERMINOS);
      await persistir();
      toast(`Importadas ${sane.length} entradas`, "success");
    } catch (err) {
      toast("Archivo JSON inválido", "error");
    } finally {
      els.fileImport.value = "";
    }
  };
  reader.readAsText(file);
}

/* ============================================================
 * Resumen del diccionario base
 * ============================================================ */

function renderCategorias() {
  if (!self.LEXICON_DEFAULT) return;
  const map = self.LEXICON_DEFAULT;
  const labels = {
    insultos: ["Insultos", "Genéricos y vulgares"],
    discriminatorios: ["Discriminatorios", "Origen, género, orientación"],
    violencia: ["Violencia", "Amenazas y agresiones"],
    latam: ["Modismos LATAM", "Variantes regionales"],
  };
  const frag = document.createDocumentFragment();
  for (const cat in map) {
    const card = document.createElement("div");
    card.className = "cat";
    const [name, sub] = labels[cat] || [cat, ""];
    card.innerHTML = `
      <div class="cat-name">${name}</div>
      <div class="cat-count">${map[cat].length}</div>
      <div class="cat-sub">${sub}</div>
    `;
    frag.appendChild(card);
  }
  els.defaultCategories.innerHTML = "";
  els.defaultCategories.appendChild(frag);
}

/* ============================================================
 * Backend API
 * ============================================================ */

function normalizarApiUrl(raw) {
  const value = String(raw || "").trim().replace(/\/+$/, "");
  if (!value) return "http://127.0.0.1:8000";
  if (!/^https?:\/\//i.test(value)) return "http://" + value;
  return value;
}

function pingApi() {
  const apiHabilitada = els.settingApi.checked;
  const url = normalizarApiUrl(els.inputApiUrl.value);

  els.apiStatusDot.classList.remove("is-on", "is-error", "is-warn");

  if (!apiHabilitada) {
    els.apiStatusDot.classList.add("is-warn");
    els.apiStatusText.textContent = "API desactivada; se usará el lexicón";
    return;
  }

  els.apiStatusText.textContent = "Comprobando modelo...";
  chrome.runtime.sendMessage({ tipo: "PING_API", url }, (res) => {
    if (chrome.runtime.lastError || !res) {
      els.apiStatusDot.classList.add("is-error");
      els.apiStatusText.textContent = "API sin conexión";
      return;
    }

    if (res.ok) {
      els.apiStatusDot.classList.add("is-on");
      els.apiStatusText.textContent = "API BETO lista";
    } else if (res.reason === "model_not_loaded") {
      els.apiStatusDot.classList.add("is-error");
      els.apiStatusText.textContent = "API activa, modelo no cargado";
    } else {
      els.apiStatusDot.classList.add("is-error");
      els.apiStatusText.textContent = "API sin conexión";
    }
  });
}

/* ============================================================
 * Toast
 * ============================================================ */

let toastTimer;
function toast(msg, kind = "success") {
  els.toast.textContent = msg;
  els.toast.classList.remove("success", "error");
  els.toast.classList.add(kind);
  els.toast.classList.add("show");
  clearTimeout(toastTimer);
  toastTimer = setTimeout(() => els.toast.classList.remove("show"), 2200);
}
