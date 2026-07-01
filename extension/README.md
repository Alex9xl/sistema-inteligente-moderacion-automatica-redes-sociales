# Detector de Discurso de Odio (ES) - Extension

Version 1.0 de la extension de navegador del proyecto de tesis.

El motor principal es la API local de BETO (`http://127.0.0.1:8000`). El
lexicon local queda como respaldo: se usa cuando la API esta desactivada, no
tiene el modelo cargado o no responde.

## Caracteristicas

- Deteccion automatica en paginas web compatibles con content scripts.
- API BETO prioritaria con verificacion de `/health` y `model_loaded`.
- Respaldo por lexicon local y lexicon personal del usuario.
- 4 modos de censura: Resaltar, Difuminar, Asteriscos y Ocultar.
- Umbral configurable para la probabilidad BETO.
- Estadisticas por pagina y total acumulado.
- Privacidad: el lexicon personal vive en `chrome.storage.local`; la API local
  recibe solo fragmentos visibles cuando esta habilitada.

## Flujo

```text
Deteccion activa
  -> API BETO habilitada y modelo cargado
      -> POST /predict
      -> censura con el modo elegido si probabilidad >= umbral
  -> API desactivada/caida/sin modelo
      -> lexicon local de respaldo
```

## Instalacion rapida

```text
1. Abre chrome://extensions o edge://extensions.
2. Activa "Modo de desarrollador".
3. Pulsa "Cargar descomprimida" y selecciona la carpeta extension/.
4. Levanta el backend: uvicorn src.api.main:app --host 127.0.0.1 --port 8000.
5. Activa la deteccion en el popup y verifica "API BETO lista".
6. Abre extension/test/demo.html para probar.
```
