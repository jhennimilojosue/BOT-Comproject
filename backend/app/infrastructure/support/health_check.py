"""
Health Check - Utilidades de verificación de salud del sistema.

Responsabilidades:
- Verificar la salud de la base de datos
- Verificar la conectividad con Ollama
- Proporcionar estado general del sistema
"""

import time
from typing import Any, Dict, Optional
from urllib.parse import urlparse

import httpx
from sqlalchemy import text
from sqlalchemy.orm import Session


class HealthChecker:
    """
    Verificador de salud del sistema.

    Attributes:
        db_session: Sesión de base de datos (opcional)
        ollama_url: URL de Ollama (opcional)
    """

    def __init__(
        self,
        db_session: Optional[Session] = None,
        ollama_url: Optional[str] = None,
    ):
        """
        Inicializa el verificador de salud.

        Args:
            db_session: Sesión de base de datos
            ollama_url: URL del servidor Ollama
        """
        self.db_session = db_session
        self.ollama_url = ollama_url or "http://localhost:11434"

    def check_database(self) -> Dict[str, Any]:
        """
        Verifica la salud de la base de datos.

        Returns:
            Diccionario con el estado de la verificación
        """
        if self.db_session is None:
            return {
                "status": "not_configured",
                "message": "Sesión de base de datos no configurada",
            }

        try:
            start_time = time.time()
            self.db_session.execute(text("SELECT 1"))
            response_time = (time.time() - start_time) * 1000  # ms

            return {
                "status": "healthy",
                "message": "Conexión exitosa",
                "response_time_ms": round(response_time, 2),
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "message": f"Error de conexión: {str(e)}",
            }

    def check_ollama(self) -> Dict[str, Any]:
        """
        Verifica la conectividad con Ollama.

        Returns:
            Diccionario con el estado de la verificación
        """
        try:
            start_time = time.time()
            response = httpx.get(f"{self.ollama_url}/api/tags", timeout=5.0)
            response_time = (time.time() - start_time) * 1000  # ms

            if response.status_code == 200:
                models = response.json().get("models", [])
                return {
                    "status": "healthy",
                    "message": "Ollama disponible",
                    "response_time_ms": round(response_time, 2),
                    "models_count": len(models),
                }
            else:
                return {
                    "status": "unhealthy",
                    "message": f"Ollama respondió con código {response.status_code}",
                }
        except httpx.ConnectError:
            return {
                "status": "unhealthy",
                "message": "No se pudo conectar a Ollama",
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "message": f"Error al verificar Ollama: {str(e)}",
            }

    def check_all(self) -> Dict[str, Any]:
        """
        Realiza todas las verificaciones de salud.

        Returns:
            Diccionario con el estado general del sistema
        """
        db_status = self.check_database()
        ollama_status = self.check_ollama()

        # Determinar estado general
        all_healthy = (
            db_status["status"] in ["healthy", "not_configured"]
            and ollama_status["status"] in ["healthy", "unhealthy"]
        )

        return {
            "status": "healthy" if all_healthy else "degraded",
            "timestamp": time.time(),
            "checks": {
                "database": db_status,
                "ollama": ollama_status,
            },
        }
