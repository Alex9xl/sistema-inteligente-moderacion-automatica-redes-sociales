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

Consulta `documentos_extras/INSTRUCCIONES_PROYECTO.md` para la especificación técnica completa.

Consulta `documentos_extras/PLAN_DESARROLLO.md` para los pasos de ejecución paso a paso.

Consulta `documentos_extras/GUIA_REPRODUCCION.md` para reproducir datos, notebooks y resultados desde cero.

## Documentos principales

- `documentos_extras/INSTRUCCIONES_PROYECTO.md` - Enunciado oficial y especificación técnica/metodológica
- `documentos_extras/PLAN_DESARROLLO.md` - Guía ejecutable paso a paso (decisiones, avances y aprendizaje)
- `documentos_extras/GUIA_REPRODUCCION.md` - Guía de replicación para evaluadores externos
- `EXPERIMENTOS.md` - Bitácora de decisiones y corridas experimentales
- `data/processed/MANIFEST.json` - Versiones y hashes de artefactos

## Licencia

MIT (modelo base BETO) + dataset académicos bajo sus respectivas licencias.
