#!/bin/bash
# Script para ejecutar el backend FastAPI

uvicorn src.api.main:app --host 127.0.0.1 --port 8000 --reload
