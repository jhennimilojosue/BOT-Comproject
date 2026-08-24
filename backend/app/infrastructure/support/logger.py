"""
Logger Configuration - Configuración de logging para el sistema.

Responsabilidades:
- Configurar el formato de logs
- Proporcionar loggers para cada módulo
- Gestionar niveles de logging
"""

import logging
import sys
from typing import Optional


def setup_logger(
    name: str,
    level: Optional[int] = None,
    format: Optional[str] = None,
) -> logging.Logger:
    """
    Configura y retorna un logger.

    Args:
        name: Nombre del logger
        level: Nivel de logging (opcional)
        format: Formato del mensaje (opcional)

    Returns:
        Logger configurado
    """
    if level is None:
        level = logging.INFO

    if format is None:
        format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

    logger = logging.getLogger(name)
    logger.setLevel(level)

    # Evitar agregar handlers múltiples
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        handler.setLevel(level)
        formatter = logging.Formatter(format)
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    return logger


# Loggers predefinidos para cada módulo
excel_logger = setup_logger("botcomproject.excel", logging.INFO)
case_logger = setup_logger("botcomproject.case", logging.INFO)
processing_logger = setup_logger("botcomproject.processing", logging.INFO)
estimation_logger = setup_logger("botcomproject.estimation", logging.INFO)
ai_logger = setup_logger("botcomproject.ai", logging.INFO)
catalog_logger = setup_logger("botcomproject.catalog", logging.INFO)
api_logger = setup_logger("botcomproject.api", logging.INFO)
