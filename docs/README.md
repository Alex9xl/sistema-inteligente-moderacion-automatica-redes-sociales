# Documentación técnica del proyecto

Esta carpeta contiene documentación **corta y autocontenida** para entender el proyecto rápidamente, sin tener que leer los documentos largos de `documentos_extras/` (que sí contienen la especificación metodológica completa, pensada como respaldo académico exhaustivo).

## Orden de lectura recomendado

1. **[`flujo_completo.md`](flujo_completo.md)** — Empieza aquí. Describe todo el pipeline de punta a punta: datos crudos, construcción del corpus, entrenamiento, API y extensión.
2. **[`arquitectura.md`](arquitectura.md)** — Cómo está diseñado el sistema (las 3 capas), qué responsabilidad tiene cada módulo y por qué se tomaron las decisiones de diseño clave.
3. **[`modelo.md`](modelo.md)** — Ficha técnica del modelo BETO ajustado: configuración exacta de entrenamiento y resultados finales frente a los baselines.
4. **[`resultados.md`](resultados.md)** — Validación de las 3 hipótesis de investigación (H1, H2, H3) con métricas y significancia estadística. Útil como referencia rápida antes de una sustentación.
5. **[`glosario.md`](glosario.md)** — Definiciones de todos los términos técnicos usados en el proyecto y en esta documentación.
6. **[`reproduccion_rapida.md`](reproduccion_rapida.md)** — Lista de comandos, en orden, para regenerar todo el proyecto desde cero (asumiendo que ya tienes `data/raw/`). Es el resumen ejecutable de `flujo_completo.md`.

## Relación con otras carpetas de documentación

| Carpeta | Propósito | Audiencia |
|---|---|---|
| `docs/` (esta carpeta) | Resumen corto y directo, para entender el proyecto en minutos. | Lectura rápida, repaso antes de la defensa. |
| `documentos_extras/` | Especificación metodológica completa (`INSTRUCCIONES_PROYECTO.md`), plan de construcción (`PLAN_DESARROLLO.md`) y guía de reproducción paso a paso (`GUIA_REPRODUCCION.md`). | Evaluador que quiere el detalle exhaustivo o reproducir el proyecto desde cero. |
| `EXPERIMENTOS.md` (raíz) | Bitácora científica con hashes, metadatos del entorno y resultados exactos de cada corrida. | Trazabilidad y verificación de resultados. |

Si algo en `docs/` y `documentos_extras/` llegara a contradecirse, `documentos_extras/INSTRUCCIONES_PROYECTO.md` y `EXPERIMENTOS.md` son la fuente de verdad; `docs/` es un resumen derivado de ambos.
