# Reportes de Control de Calidad

Este directorio contiene reportes automáticos de validación de datos.

## Estructura

```
data/reports_qc/
├── qc_corpus_v1.md                 # Reporte del corpus v1
├── qc_corpus_v1.png                # Visualizaciones
├── README.md
```

## Contenido esperado

Cada reporte QC incluye:

- Distribución de clases
- Distribución de `tiene_modismo`
- Longitudes de texto (mediana, percentiles)
- Top tokens/bigramas por clase
- Conteos de duplicados eliminados
- Verificación de fuga train↔test

## Generación

Los reportes se generan automáticamente desde:

```python
from src.data.qc import generar_reporte_qc

generar_reporte_qc(corpus, version=1)
```

O desde el notebook: `notebooks/02_unificacion.ipynb`
