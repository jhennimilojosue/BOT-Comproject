"""
Configuration - Gestión de configuración del sistema.

Responsabilidades:
- Cargar variables de entorno
- Proporcionar configuración centralizada
- Validar configuración requerida
"""

import os
from dataclasses import dataclass
from typing import Optional

from dotenv import load_dotenv


@dataclass
class DatabaseConfig:
    """Configuración de la base de datos."""
    url: str
    pool_size: int = 10
    max_overflow: int = 20


@dataclass
class OllamaConfig:
    """Configuración de Ollama."""
    base_url: str
    model: str
    timeout: int = 60


@dataclass
class AppConfig:
    """Configuración de la aplicación."""
    env: str
    debug: bool
    host: str
    port: int


@dataclass
class Settings:
    """
    Configuración centralizada del sistema.

    Attributes:
        database: Configuración de la base de datos
        ollama: Configuración de Ollama
        app: Configuración de la aplicación
    """
    database: DatabaseConfig
    ollama: OllamaConfig
    app: AppConfig


def load_settings(env_file: Optional[str] = None) -> Settings:
    """
    Carga la configuración desde variables de entorno.

    Args:
        env_file: Ruta al archivo .env (opcional)

    Returns:
        Configuración cargada
    """
    if env_file:
        load_dotenv(env_file)
    else:
        load_dotenv()

    # Database
    database_url = os.getenv(
        "DATABASE_URL",
        "postgresql://postgres:postgres@localhost:5432/bot_comproject"
    )
    db_pool_size = int(os.getenv("DB_POOL_SIZE", "10"))
    db_max_overflow = int(os.getenv("DB_MAX_OVERFLOW", "20"))

    # Ollama
    ollama_base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    ollama_model = os.getenv("OLLAMA_MODEL", "qwen2.5-coder:3b")
    ollama_timeout = int(os.getenv("OLLAMA_TIMEOUT", "60"))

    # App
    app_env = os.getenv("APP_ENV", "development")
    app_debug = os.getenv("APP_DEBUG", "true").lower() == "true"
    app_host = os.getenv("APP_HOST", "0.0.0.0")
    app_port = int(os.getenv("APP_PORT", "8000"))

    return Settings(
        database=DatabaseConfig(
            url=database_url,
            pool_size=db_pool_size,
            max_overflow=db_max_overflow,
        ),
        ollama=OllamaConfig(
            base_url=ollama_base_url,
            model=ollama_model,
            timeout=ollama_timeout,
        ),
        app=AppConfig(
            env=app_env,
            debug=app_debug,
            host=app_host,
            port=app_port,
        ),
    )


# Instancia global de configuración
settings = load_settings()
