"""Configuración de la API."""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    model_dir: str = "models/beto_finetuned_final"
    model_version: str = "v1"
    max_input_chars: int = 512
    threshold: float = 0.5
    allowed_origins: list[str] = [
        "chrome-extension://*",
        "http://localhost:8000",
        "http://127.0.0.1:8000",
    ]
    log_level: str = "INFO"

    class Config:
        env_file = ".env"


settings = Settings()
