# Guía de la Extensión — Detector de Discurso de Odio (ES)

**Versión:** 0.9.0 (`version_name: "0.9.0-beta"`) · prototipo funcional
**Carpeta:** `extension/`
**Modo actual:** detección por **lexicón local** (sin backend BETO).
La conexión con la API de BETO ajustado quedará habilitada más adelante,
cuando el modelo esté disponible en `http://127.0.0.1:8000`.

Esta guía explica cómo cargar, configurar y probar la beta en
**Google Chrome**, **Microsoft Edge** o cualquier navegador basado en
Chromium.

> **Nota sobre el manifest.json**
> Chrome/Edge exigen que `version` sea **1–4 enteros separados por
> puntos** (cada uno entre 0 y 65535). Por eso el manifiesto declara:
> ```json
> "version": "0.9.0",
> "version_name": "0.9.0-beta"
> ```
> El campo `version_name` es el que se muestra al usuario; `version` es
> el que valida el navegador. Si vuelves a tocar el manifiesto, **no**
> pongas sufijos tipo `-beta`, `-rc1` o letras en `version`: el
> navegador rechazará la extensión con el error “Required value
> 'version' is missing or invalid”.

---

## 1. Requisitos

- **Navegador:** Chrome ≥ 110 o Edge ≥ 110.
- **(Opcional) Python ≥ 3.10** con `Pillow`, sólo si quieres regenerar los
  iconos. Los iconos ya vienen incluidos en `extension/icons/`.

```bash
# (Opcional) regenerar iconos
cd extension
pip install pillow
python icons/generate_icons.py
```

---

## 2. Estructura de la extensión

```
extension/
├── manifest.json        ← Manifest V3
├── lexicon.js           ← Diccionario base + utilidades de matching
├── api.js               ← Contrato con backend BETO (stub funcional)
├── content.js           ← Escaneo del DOM + censura
├── background.js        ← Service worker, badge, estadísticas, cola BETO
├── styles.css           ← Estilos inyectados en las páginas
├── popup/
│   ├── popup.html       ← UI principal (toggle, stats, modos)
│   ├── popup.css
│   └── popup.js
├── options/
│   ├── options.html     ← Lexicón personal + ajustes avanzados
│   ├── options.css
│   └── options.js
├── icons/               ← icon16/32/48/128.png
└── test/
    └── demo.html        ← Página local con texto de prueba
```

---

## 3. Instalación paso a paso

### 3.1 Cargar la extensión sin empaquetar

1. Abre tu navegador y entra en:
   - Chrome: `chrome://extensions`
   - Edge: `edge://extensions`
2. Activa **Modo de desarrollador** (esquina superior derecha).
3. Pulsa **Cargar descomprimida** (Chrome) / **Cargar descomprimido** (Edge).
4. Selecciona la carpeta:
   ```
   c:\Users\vanau\Documents\Proyectos\Tesis_Proyecto\extension
   ```
5. La extensión aparece como **“Detector de Discurso de Odio (ES)”**.
   Fija su icono en la barra para acceso rápido.

### 3.2 Conceder permisos

La extensión declara estos permisos:

| Permiso              | Por qué se usa                                                                  |
| -------------------- | ------------------------------------------------------------------------------- |
| `storage`            | Guardar configuración y lexicón personal.                                       |
| `activeTab`          | Re-escanear la pestaña actual cuando pulsas “Re-escanear”.                      |
| `scripting`          | Inyectar el `content.js` en páginas activas.                                    |
| `host_permissions` → `http://127.0.0.1:8000/*` | Solo para el ping al backend BETO (futuro). |

> No se piden permisos para enviar datos a Internet. Toda la detección de
> esta beta es local.

---

## 4. Uso básico

1. Pulsa el icono de la extensión → aparece el **popup**.
2. Activa el interruptor **“Detección automática”**.
3. Selecciona el **modo de censura**:
   - **Resaltar** (por defecto): subraya en rojo las coincidencias.
   - **Difuminar**: aplica blur; clic para revelar.
   - **Asteriscos**: reemplaza por `***`.
   - **Ocultar**: muestra `[contenido oculto]`; clic para revelar.
4. Navega normalmente. La detección se aplica al instante.
5. El **badge** del icono muestra el número de detecciones de la pestaña.

> Si modificas la lista o el modo y no ves cambios, pulsa
> **Re-escanear** en el popup. Si la página usa frameworks pesados
> (Twitter/X, Reddit, etc.) puede tardar 1–2 segundos en repintar.

---

## 5. Probar la beta sin redes sociales

Hay una página local de pruebas con textos representativos.

### Opción A · abrirla con `file://`

1. En el explorador de archivos, ve a:
   ```
   c:\Users\vanau\Documents\Proyectos\Tesis_Proyecto\extension\test\demo.html
   ```
2. Doble clic. Se abre en el navegador.
3. Activa la extensión y observa cómo se censuran los términos.

> **Importante (Chrome):** para que un content script se ejecute en URLs
> `file://`, ve a `chrome://extensions`, abre los **detalles** de la
> extensión y activa **“Permitir acceso a URLs de archivo”**.

### Opción B · servirla con un servidor local

Desde la raíz del proyecto:

```bash
python -m http.server 8080
# Luego abre:
# http://localhost:8080/extension/test/demo.html
```

No requiere permisos especiales.

---

## 6. Lexicón personal (Options Page)

Pulsa **Lexicón** en el popup, o clic derecho sobre el icono → **Opciones**.

### Funciones disponibles

- **Agregar** un término o frase corta (máx. 64 caracteres, hasta 200 entradas).
- **Buscar** en tu lista.
- **Quitar** un término haciendo clic en la “×” del chip.
- **Borrar todo** (con confirmación).
- **Exportar** tu lista a un archivo JSON (`lexicon-personal-AAAA-MM-DD.json`).
- **Importar** un JSON previamente exportado (se mezcla, no se duplica).
- **Restaurar** vacía la lista personal y resetea ajustes a por defecto.

### Ajustes adicionales

- **Detección automática:** mismo toggle que el popup.
- **Diccionario base:** combinarlo o usar sólo tu lista.
- **Modo de censura:** mismo selector que el popup, en formato dropdown.
- **Backend BETO:**
  - **Habilitar API:** placeholder para integración futura.
  - **URL del backend:** por defecto `http://127.0.0.1:8000`.

### Privacidad

El lexicón personal se guarda **solo** en `chrome.storage.local`. No se
sincroniza con ningún servidor ni siquiera con tu cuenta de Google. Para
mover tu lista entre equipos, usa **Exportar → Importar**.

---

## 7. Diccionario base por defecto

Definido en `extension/lexicon.js`:

| Categoría          | Aprox. términos | Ejemplos representativos                |
| ------------------ | :-------------: | --------------------------------------- |
| `insultos`         |       ~30       | idiota, imbécil, hijo de puta, mierda   |
| `discriminatorios` |       ~22       | maricón, sudaca, naco, feminazi         |
| `violencia`        |       ~17       | te mato, ojalá te mueras, te reviento   |
| `latam`            |       ~25       | weón culiao, conchatumadre, no mames    |

Para añadir términos al diccionario base, edita `extension/lexicon.js` y
recarga la extensión desde `chrome://extensions`.

> Para términos personales, usa la **Options Page**. Es lo recomendado.

---

## 8. Modos de censura — equivalencia visual

| Modo            | Texto original "idiota"     | CSS aplicado                          |
| --------------- | --------------------------- | ------------------------------------- |
| `highlight`     | <u>idiota</u> (subrayado rojo) | `background` rojo translúcido        |
| `blur`          | <span style="filter:blur(4px)">idiota</span> | `filter: blur(5px)`                   |
| `asterisk`      | `******`                    | reemplazo de texto, fondo oscuro      |
| `hide`          | `[contenido oculto]`        | reemplazo, gris itálico, clic muestra |

Los modos `blur` y `hide` permiten **clic para revelar** sin desactivar la
detección.

---

## 9. Recargar la extensión tras cambios

Si modificas archivos `.js`, `.html` o `.css`:

1. Ve a `chrome://extensions`.
2. Pulsa el botón **↻** (recargar) en la tarjeta de la extensión.
3. Recarga la pestaña donde estás probando (`F5`).

Si modificas el `manifest.json` siempre **recarga** la extensión.

---

## 10. Solución de problemas

| Síntoma                                       | Causa probable                                         | Solución                                                                  |
| --------------------------------------------- | ------------------------------------------------------ | ------------------------------------------------------------------------- |
| El popup se abre pero no detecta nada         | El interruptor está apagado                            | Activa **“Detección automática”**                                         |
| `chrome://...` no detecta nada                | Chrome bloquea content scripts en sus páginas internas | Es esperado. Prueba en `demo.html` o un sitio normal                      |
| `file://...` no detecta nada                  | No hay permiso para archivos locales                   | En `chrome://extensions` → detalles → activa **“acceso a URLs de archivo”** |
| “Sin conexión (modo lexicón)” en el popup      | El backend BETO no está corriendo                      | Es lo esperado en la beta. La detección por lexicón funciona igual         |
| Texto detectado pero el badge no se actualiza | El service worker se durmió                            | Pulsa **Re-escanear**, o reabre el popup                                   |
| Los chips desaparecen al refrescar la página  | No deberían                                            | Verifica `chrome://extensions` → no se haya borrado el storage             |

Para depurar:

- **Service worker** (`background.js`):
  `chrome://extensions` → tarjeta → **inspeccionar vista** → *service worker*.
- **Popup** y **Options**: clic derecho sobre el popup/options → **Inspeccionar**.
- **Content script**: DevTools de la página → consola → filtro
  `[Detector ES]` o errores.

---

## 11. Estado actual de la integración con BETO

| Componente                       | Estado                                            |
| -------------------------------- | ------------------------------------------------- |
| Lexicón local                    | ✅ Funcionando                                    |
| 4 modos de censura               | ✅ Funcionando                                    |
| Lexicón personal (CRUD + I/O)    | ✅ Funcionando                                    |
| Estadísticas (página + total)    | ✅ Funcionando                                    |
| Ping al backend (`/health`)      | ✅ Implementado vía `HateApi.apiHealth`           |
| Cliente HTTP `apiPredict/apiExplain` | ✅ Implementado en `api.js` (sin invocar)     |
| Cola con concurrencia + backoff  | ✅ Implementado en `api.js`                       |
| Caché en memoria (TTL 5 min)     | ✅ Implementado en `api.js`                       |
| Handler `PREDICT_BATCH` en SW    | ✅ Implementado, gateado por `apiHabilitada`      |
| Handler `EXPLAIN_REQ` en SW      | ✅ Implementado, gateado por `apiHabilitada`      |
| Inferencia real con BETO         | ⏳ Espera el modelo entrenado (Fase 3 de la tesis) |
| XAI con SHAP en el DOM           | ⏳ Falta CSS `.hate-ml`, `.hate-explain-token`    |

### 11.1 Qué archivos modificar cuando BETO esté listo

Todo el cableado ya está hecho. Solo queda **rellenar los stubs** marcados
con la etiqueta `TODO BETO` en el código. El orden recomendado es:

| # | Archivo                       | Qué hacer                                                                                                       |
| - | ----------------------------- | --------------------------------------------------------------------------------------------------------------- |
| 1 | `src/api/main.py`             | Levantar FastAPI con el modelo `models/beto_finetuned_final` (ver `desarrollo.md` Fase 6 / `guia.md` §14).      |
| 2 | `extension/options/options.html` (UI) + `chrome.storage.local` | Activar el toggle **“Habilitar API”** → escribe `apiHabilitada=true`. **No hace falta tocar código.**           |
| 3 | `extension/content.js`        | En `escanear()`, después del bloque del lexicón, construir un arreglo de fragmentos `{id, texto}` (≤512 chars c/u, máx 50 por escaneo) y llamar a `enviarLoteAlModelo(fragmentos)`. Guardar la referencia al nodo en `window.__hateRefs[id]` para localizarlo al recibir el `RESULTADO`. |
| 4 | `extension/content.js`        | Escuchar `chrome.runtime.onMessage` para `tipo === "RESULTADO"` y llamar a `aplicarResultadoML(msg)`. Implementar esa función para envolver el nodo en `<mark class="hate-ml" title="p=0.93">` cuando `probabilidad >= umbralMl`. |
| 5 | `extension/styles.css`        | Añadir reglas `.hate-ml` (subrayado/fondo rojo intenso) y `.hate-explain-token` para tokens SHAP, según `guia.md` §15.10. |
| 6 | `extension/background.js`     | Nada. Los handlers `PREDICT_BATCH` y `EXPLAIN_REQ` ya delegan en `HateApi` y respetan `apiHabilitada`.           |
| 7 | `extension/api.js`            | Nada. El contrato HTTP, la cola y el caché ya están implementados según `guia.md` §15.6 / §15.9 / §15.11.       |
| 8 | `extension/popup/popup.html` (opcional) | Reactivar el slider de **umbral** (referencia en `guia.md` §15.7). En la beta se ocultó por no usarse aún. |

### 11.2 Búsqueda rápida de los puntos a tocar

Ejecuta en la raíz del repo para listar todos los marcadores que quedan
por activar:

```powershell
findstr /S /N /I "TODO BETO" extension\*.js
```

Salida esperada (resumen): los stubs `enviarLoteAlModelo`,
`aplicarResultadoML`, los `case "PREDICT_BATCH"` / `case "EXPLAIN_REQ"`
en el service worker y los comentarios de bloque que documentan la
integración.

### 11.3 Smoke test end-to-end (cuando BETO esté listo)

1. Levantar el backend:
   `uvicorn src.api.main:app --host 127.0.0.1 --port 8000 --reload`
2. Verificar Swagger: `http://127.0.0.1:8000/docs`.
3. En la **Options Page** marcar **“Habilitar API”** (escribe
   `apiHabilitada=true` en `chrome.storage.local`).
4. Recargar la extensión en `chrome://extensions`.
5. Abrir `extension/test/demo.html`. El popup debe mostrar
   **“Backend disponible”** y, además del subrayado del lexicón, deben
   aparecer marcas con `class="hate-ml"` en los fragmentos que el modelo
   clasifique como hate con `probabilidad ≥ umbralMl`.

---

## 12. Empaquetado para distribución (opcional)

Para un `.zip` listo para Chrome Web Store / instalación manual:

```powershell
cd c:\Users\vanau\Documents\Proyectos\Tesis_Proyecto
Compress-Archive -Path extension\* -DestinationPath detector-es-v0.9.0-beta.zip -Force
```

> Para una entrega oficial al Web Store harán falta políticas, ID de
> publisher, capturas y descripción. Eso queda **fuera del alcance**
> de la tesis (sección 2.4 de `guia.md`).

---

## 13. Resumen de comandos útiles

```powershell
# 1) (Opcional) regenerar iconos
cd extension
python icons/generate_icons.py

# 2) Servir la página de prueba
cd ..
python -m http.server 8080
# Abrir http://localhost:8080/extension/test/demo.html

# 3) Empaquetar para distribución manual
Compress-Archive -Path extension\* -DestinationPath detector-es-v0.9.0-beta.zip -Force
```

---

## 14. Checklist rápida de validación

- [ ] La extensión se carga sin errores en `chrome://extensions`.
- [ ] El popup se abre y muestra el interruptor.
- [ ] Activando la detección y abriendo `test/demo.html`, hay coincidencias.
- [ ] Cambiar el modo (Resaltar → Asteriscos) repinta inmediatamente al pulsar “Re-escanear”.
- [ ] La Options Page permite agregar/quitar términos y persiste tras recargar.
- [ ] Exportar/Importar JSON funciona.
- [ ] Desactivar la detección elimina las marcas de la página.

Si los 7 puntos están ✓, la beta está lista para mostrar como
demostración funcional en la defensa, mientras se completa el
fine-tuning del modelo BETO.
