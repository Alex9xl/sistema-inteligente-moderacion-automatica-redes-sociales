# Decisiones de Diseño

Justificaciones para cada decisión arquitectónica y metodológica.

## Decisiones clave

Ver `guia.md` sección 3.6 para tabla completa de decisiones vs alternativas.

### BETO cased vs uncased

**Decisión:** Usar BETO `cased`

**Justificación:** El discurso de odio explota patrones de mayúsculas (gritos, énfasis). La versión `uncased` destruiría esta señal.

### Etiquetado binario

**Decisión:** Hate / No hate (sin subcategorías)

**Justificación:** Facilita comparación entre datasets con esquemas distintos. Análisis fino de tipos puede hacerse post-hoc.

### Lexicón como feature observable, no como input

**Decisión:** Usar lexicón LATAM solo para marcar `tiene_modismo`, no para aumentar el input del modelo

**Justificación:** Permite evaluar el modelo como caja negra. El lexicón se usa para segmentar la evaluación (H3).

## Riesgos mitigados

Ver `guia.md` sección 3.7 para matriz de riesgos arquitectónicos.
