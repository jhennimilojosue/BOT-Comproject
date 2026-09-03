"""
BOT-COMProject - Main Application

Aplicación principal de FastAPI para el sistema BOT-COMProject.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .infrastructure.support.config import settings
from .api.routes import uploads, processing, responsible, results, export, ai
from .infrastructure.support.health_check import HealthChecker

# Crear aplicación
app = FastAPI(
    title="BOT-COMProject API",
    description="API para el procesamiento de casos de Aranda",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluir rutas
app.include_router(uploads.router)
app.include_router(processing.router)
app.include_router(responsible.router)
app.include_router(results.router)
app.include_router(export.router)
app.include_router(ai.router)


@app.get("/", tags=["root"])
async def root():
    """
    Endpoint raíz de la API.

    Returns:
        Mensaje de bienvenida
    """
    return {
        "message": "BOT-COMProject API",
        "version": "1.0.0",
        "docs": "/docs",
    }


@app.get("/health", tags=["health"])
async def health_check():
    """
    Verifica la salud del sistema.

    Returns:
        Estado del sistema
    """
    from .api.dependencies import get_db
    from sqlalchemy.orm import Session
    
    db = next(get_db())
    try:
        checker = HealthChecker(db_session=db)
        return checker.check_all()
    finally:
        db.close()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host=settings.app.host,
        port=settings.app.port,
        reload=settings.app.debug,
    )
