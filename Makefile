.PHONY: help install data train evaluate api test lint clean

help:
	@echo "Comandos disponibles:"
	@echo "  make install    - Instalar dependencias"
	@echo "  make data       - Preparar corpus unificado"
	@echo "  make train      - Entrenar BETO ajustado y baselines (3 semillas)"
	@echo "  make evaluate   - Evaluar modelos en test set"
	@echo "  make api        - Ejecutar backend FastAPI"
	@echo "  make test       - Ejecutar tests unitarios e integración"
	@echo "  make lint       - Verificar código (ruff + black)"
	@echo "  make clean      - Limpiar directorios de cache"

install:
	pip install -r requirements.txt
	pre-commit install

data:
	python scripts/prepare_data.py --version 1

train:
	python scripts/train_model.py --model beto --seed 42
	python scripts/train_model.py --model beto --seed 123
	python scripts/train_model.py --model beto --seed 2024
	python scripts/train_model.py --model mbert --seed 42
	python scripts/train_model.py --model mbert --seed 123
	python scripts/train_model.py --model mbert --seed 2024
	python scripts/train_model.py --model xlmr --seed 42
	python scripts/train_model.py --model xlmr --seed 123
	python scripts/train_model.py --model xlmr --seed 2024

evaluate:
	python scripts/evaluate_model.py --all

api:
	uvicorn src.api.main:app --host 127.0.0.1 --port 8000 --reload

test:
	pytest --cov=src --cov-report=term-missing -v

lint:
	ruff check src tests scripts
	black --check src tests scripts

clean:
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	rm -rf build/ dist/ *.egg-info/
	rm -rf reports/logs/*
