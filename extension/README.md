# Detector de Discurso de Odio (ES) — Extensión

Beta funcional (v0.9.0) de la extensión de navegador del proyecto de tesis.

> Modo prototipo: detección 100% local con un **lexicón** de términos en
> español (neutro + LATAM). La integración con el modelo BETO ajustado vía
> API local (FastAPI) está reservada para cuando el modelo esté disponible.

## Características

- Detección automática en cualquier página web (Manifest V3).
- 4 modos de censura: **Resaltar**, **Difuminar**, **Asteriscos**, **Ocultar**.
- Lexicón base con ~80 términos repartidos en 4 categorías.
- Lexicón personal del usuario (CRUD, búsqueda, importar/exportar JSON).
- Estadísticas: detecciones por página, total acumulado, cantidad de palabras propias.
- Privacidad: el lexicón personal vive sólo en `chrome.storage.local`.
- UI moderna en tema violeta con glassmorphism.

## Estructura

```
extension/
├── manifest.json
├── lexicon.js
├── content.js
├── background.js
├── styles.css
├── popup/
│   ├── popup.html
│   ├── popup.css
│   └── popup.js
├── options/
│   ├── options.html
│   ├── options.css
│   └── options.js
├── icons/
│   ├── icon16.png  icon32.png  icon48.png  icon128.png
│   └── generate_icons.py
└── test/
    └── demo.html       (página de prueba local)
```

## Instalación rápida

Ver `documentos_extras/guia-extension.md` para la guía paso a paso.

```text
1. Abre chrome://extensions  (o edge://extensions)
2. Activa "Modo de desarrollador"
3. Pulsa "Cargar descomprimida" y selecciona la carpeta extension/
4. Abre el popup, activa la detección
5. Abre extension/test/demo.html para probar
```
