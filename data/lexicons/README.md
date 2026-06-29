# Lexicones

Este directorio contiene recursos léxicos para enriquecimiento y análisis.

## Estructura

```
data/lexicons/
├── modismos_latam_v1.csv              # Lexicón de investigación
├── modismos_latam_v2.csv              # Versiones posteriores (si aplica)
├── README.md
└── CHANGELOG.md
```

## Lexicón LATAM

**Archivo:** `modismos_latam_v1.csv`

**Columnas:**
- `termino`: Forma canónica en minúsculas
- `variantes`: Variantes separadas por `;`
- `pais`: Código ISO (MX, AR, CL, CO, PE, VE, etc.) o `MULTI`
- `tipo`: Categoría (coloquial, intensificador, insulto, despectivo, juvenil)
- `fuente`: Origen (ASALE, literatura, curado_manual)
- `notas`: Aclaraciones de uso
- `version_introduccion`: Versión del lexicón en la que aparece

**Tamaño mínimo:** ≥ 500 términos

**Cobertura esperada:** ≥ 15% del corpus debe marcar `tiene_modismo = True`

## Uso

```python
from src.data.lexicon import LexiconLatam

lexicon = LexiconLatam("data/lexicons/modismos_latam_v1.csv")
tiene = lexicon.tiene_modismo("Ese pinche wey es un ñero")  # True
```

## Importante

Este lexicón es de **investigación** (sección 8 de `documentos_extras/INSTRUCCIONES_PROYECTO.md`). 

Distinto del **lexicón personal del usuario** (que vive en la extensión Chrome, sección 15).

No confundir ni mezclar en documentación.
