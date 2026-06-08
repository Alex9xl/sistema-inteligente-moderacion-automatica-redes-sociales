# Guía de Arquitectura

Descripción de la arquitectura del sistema y sus componentes.

## Diagrama general

[Ver `guia.md` sección 3.2 para diagrama ASCII completo]

## Capas funcionales

1. **Capa de Datos**: Preparación, limpieza, unificación de corpus
2. **Capa de Modelado**: Entrenamiento de BETO, mBERT, XLM-R
3. **Capa de Evaluación**: Métricas, tests estadísticos
4. **Capa de Servicio**: API REST FastAPI
5. **Capa de Cliente**: Extensión Chrome Manifest V3

## Dependencias entre módulos

Ver `guia.md` sección 3.5 para matriz completa de dependencias.
