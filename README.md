# Sistema Inteligente de Moderación Automática en Redes Sociales

Tesis realizada por

- Quiñonez Rivera Esteban
- Palomino Julian Alex Marcelo

Para obtener el Grado Académico de Bachiller en Ingeniería de Software

Detección automática de discurso de odio en español mediante BETO ajustado, modelos multilingües de referencia y una extensión de navegador.

## Inicio rápido

### Instalación del entorno

```bash
python -m venv venv
source venv/Scripts/activate  # En Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### Preparar datos

```bash
make data
```

### Entrenar modelo

```bash
make train
```

### Ejecutar API

```bash
make api
```

### Ejecutar tests

```bash
make test
```

## Estructura del proyecto

Consulta `guia.md` para la especificación técnica completa.

Consulta `desarrollo.md` para los pasos de ejecución paso a paso.

## Documentos principales

- `guia.md` - Especificación técnica y metodológica completa
- `EXPERIMENTOS.md` - Bitácora de decisiones y corridas experimentales
- `desarrollo.md` - Guía ejecutable paso a paso
- `data/processed/MANIFEST.json` - Versiones y hashes de artefactos

## Licencia

MIT (modelo base BETO) + dataset académicos bajo sus respectivas licencias.
