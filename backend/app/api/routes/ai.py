"""
AI Routes - Endpoints para servicios de IA.

Responsabilidades:
- Generar descripciones usando IA
- Estimar tiempos usando IA
- Procesar casos por responsable con WebSocket
- Consultar catálogo de tiempos
- Consultar resultados guardados
"""

import time
import uuid
from collections import defaultdict
from datetime import datetime, timedelta, timezone
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, WebSocket, WebSocketDisconnect
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from ...api.schemas.ai import (
    AIResultResponse,
    CatalogCategory,
    CatalogResponse,
    GetResultsResponse,
    ProcessResponsibleRequest,
    ProcessResponsibleResponse,
    ProcessingSummary,
    WebSocketMessage,
    WeekInfo,
)
from ...api.websocket import ConnectionManager
from ...infrastructure.ai.ai_service import AIService
from ...infrastructure.ai.models import AIConfig
from ...infrastructure.ai.ollama_provider import OllamaProvider
from ...infrastructure.ai.response_parser import ResponseParser
from ...infrastructure.support.config import settings
from ..dependencies import get_db
from ...infrastructure.database.models.case import CaseModel
from ...infrastructure.database.models.processing import ProcessingModel
from ...infrastructure.repositories.ai_result_repository import SQLAlchemyAIResultRepository
from ...infrastructure.repositories.catalogo_tiempos_repository import SQLAlchemyCatalogoTiempoRepository

router = APIRouter(prefix="/api/v1/ai", tags=["ai"])

# Instancia del parser
parser = ResponseParser()

# WebSocket manager global
ws_manager = ConnectionManager()

# Estados procesables según catálogo V1 (status_catalog.py): Solucionado y Cerrado
from ...infrastructure.catalogs.status_catalog import StatusCatalog

PROCESSABLE_STATUSES = StatusCatalog().get_all_processable()


def _format_fecha(dt):
    """Formatea una fecha de solución a YYYY-MM-DD (o None)."""
    if dt is None:
        return None
    return dt.strftime("%Y-%m-%d") if hasattr(dt, "strftime") else str(dt)


def _group_results_by_area(results):
    """Agrupa resultados de IA por área y por fecha de solución.

    Estructura: { área: { total_hours, by_date: { 'YYYY-MM-DD': { total_hours, cases: [...] } },
                          sin_fecha: { total_hours, cases: [...] } } }
    Los casos sin área van a 'Sin área' y los sin fecha a 'sin_fecha'.
    """
    grouped = {}
    for r in results:
        key = r.area or "Sin área"
        area_group = grouped.setdefault(
            key, {"total_hours": 0.0, "by_date": {}, "sin_fecha": {"total_hours": 0.0, "cases": []}}
        )
        hours = r.estimated_minutes / 60
        area_group["total_hours"] += hours
        if r.fecha_solucion:
            date_group = area_group["by_date"].setdefault(
                r.fecha_solucion, {"total_hours": 0.0, "cases": []}
            )
            date_group["total_hours"] += hours
            date_group["cases"].append(r)
        else:
            area_group["sin_fecha"]["total_hours"] += hours
            area_group["sin_fecha"]["cases"].append(r)
    return grouped


# ============================================================================
# WEBSOCKET ENDPOINT
# ============================================================================


@router.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    """
    Endpoint WebSocket para progreso en tiempo real.

    Args:
        client_id: ID único del cliente
    """
    await ws_manager.connect(websocket, client_id)
    try:
        while True:
            # Mantener conexión viva
            data = await websocket.receive_text()
            # Echo para keepalive
            if data == "ping":
                await ws_manager.send_progress(client_id, {"type": "pong"})
    except WebSocketDisconnect:
        await ws_manager.disconnect(client_id)


@router.post(
    "/process-responsible",
    response_model=ProcessResponsibleResponse,
    summary="Procesar casos de un responsable con IA",
    description="Procesa todos los casos de un responsable que estén en el catálogo, generando descripción con IA y tiempo del catálogo.",
)
def process_responsible(
    request: ProcessResponsibleRequest,
    db: Session = Depends(get_db),
):
    """Procesa los casos síncronamente inline con httpx."""
    import httpx

    try:
        catalog_repo = SQLAlchemyCatalogoTiempoRepository(db)
        all_catalog_paths = catalog_repo.get_all_paths()

        if not all_catalog_paths:
            raise HTTPException(status_code=404, detail={"error": "CATALOG_EMPTY", "message": "El catálogo de tiempos está vacío"})

        cases = (
            db.query(CaseModel)
            .filter(
                CaseModel.upload_id == request.upload_id,
                CaseModel.responsible_name == request.responsible_name,
                CaseModel.case_type.in_(["Incidente", "Requerimiento"]),
                CaseModel.status.in_(PROCESSABLE_STATUSES),
            )
            .all()
        )

        if not cases:
            raise HTTPException(status_code=404, detail={"error": "NO_CASES_FOUND", "message": f"No se encontraron casos procesables (estados {','.join(PROCESSABLE_STATUSES)}) para '{request.responsible_name}'"})

        processable_cases = [
            c for c in cases
            if catalog_repo.find_by_path(c.final_category, c.case_type)
        ]

        if not processable_cases:
            raise HTTPException(status_code=404, detail={"error": "NO_CASES_IN_CATALOG", "message": "Ningún caso está en el catálogo de tiempos"})

        # Reutilizar el processing del archivo (creado al subir el upload).
        # Todos los responsables procesados se acumulan bajo este mismo processing_id.
        processing = (
            db.query(ProcessingModel)
            .filter(ProcessingModel.upload_id == request.upload_id)
            .first()
        )
        if processing is None:
            raise HTTPException(
                status_code=404,
                detail={
                    "error": "PROCESSING_NOT_FOUND",
                    "message": "El archivo no tiene un processing asociado. Súbelo por POST /api/v1/uploads para generarlo.",
                },
            )
        processing_id = processing.id
        processing.status = "processing"
        processing.started_at = datetime.now(timezone.utc)
        db.commit()
        db.refresh(processing)

        config = AIConfig(model=settings.ollama.model, timeout=settings.ollama.timeout)
        provider = OllamaProvider(base_url=settings.ollama.base_url)
        ai_service = AIService(ai_provider=provider, config=config)
        ai_result_repo = SQLAlchemyAIResultRepository(db)

        results = []
        results_count = 0
        rejected = 0

        print(f"[DEBUG] processable_cases count: {len(processable_cases)}")
        for idx, case in enumerate(processable_cases):
            try:
                matched_category = catalog_repo.find_by_path(case.final_category, case.case_type)
                time_range = catalog_repo.get_time_range(case.final_category, case.case_type)
                if time_range is None:
                    rejected += 1
                    continue
                estimated_minutes = (time_range["min"] + time_range["max"]) // 2
                catalog_item = case.final_category.split(".")[-1]
                if matched_category:
                    catalog_item = (
                        matched_category.nivel3
                        or matched_category.path_completo.split(".")[-1]
                    )

                case_data = {
                    "case_code": case.case_code,
                    "case_type": case.case_type,
                    "final_category": case.final_category,
                    "description": case.description,
                    "solution": case.solution or "",
                }

                prompt = ai_service._build_description_context(case_data)
                start_time = time.time()

                with httpx.Client(timeout=config.timeout) as client:
                    response = client.post(
                        f"{provider.base_url}/api/generate",
                        json={
                            "model": config.model,
                            "prompt": prompt,
                            "stream": False,
                            "options": {"temperature": config.temperature, "num_predict": config.max_tokens},
                        },
                    )
                    response.raise_for_status()
                    data = response.json()
                    latency_ms = (time.time() - start_time) * 1000
                    ai_content = data.get("response", "")
                    tokens_used = data.get("eval_count", 0)

                print(f"[DEBUG] Case {case.case_code}: ai_content_len={len(ai_content)}, status={response.status_code}")

                if ai_content:
                    parsed = parser.parse_description(ai_content)
                    generated_description = parsed.text

                    ai_result_repo.save(
                        processing_id=processing_id,
                        case_id=case.id,
                        case_code=case.case_code,
                        estimated_minutes=estimated_minutes,
                        generated_description=generated_description,
                        model_name=config.model,
                        tokens_used=tokens_used,
                        latency_ms=latency_ms,
                        case_type=case.case_type,
                        status=case.status,
                        final_category=case.final_category,
                    )
                    results_count += 1

                    results.append(AIResultResponse(
                        case_code=case.case_code,
                        final_category=case.final_category,
                        catalog_category=catalog_item,
                        status=case.status,
                        case_type=case.case_type,
                        cliente=case.user_name,
                        area=case.area,
                        fecha_solucion=_format_fecha(case.fecha_solucion),
                        original_description=case.description,
                        solution=case.solution,
                        generated_description=generated_description,
                        estimated_minutes=estimated_minutes,
                        model_name=config.model,
                        tokens_used=tokens_used,
                        latency_ms=latency_ms,
                    ))
                else:
                    rejected += 1
            except Exception as e:
                rejected += 1

        processing.status = "completed"
        total_results_db = ai_result_repo.count_by_processing(processing_id)
        processing.processed_cases = total_results_db
        processing.rejected_cases = (processing.rejected_cases or 0) + rejected
        processing.completed_at = datetime.now(timezone.utc)
        db.commit()

        total_minutes = sum(r.estimated_minutes for r in results)
        total_hours = total_minutes / 60
        avg_minutes = total_minutes / len(results) if results else 0

        by_type = defaultdict(lambda: {"count": 0, "hours": 0})
        by_category = defaultdict(lambda: {"count": 0, "hours": 0})
        by_area = defaultdict(lambda: {"count": 0, "hours": 0})
        for r in results:
            by_type[r.case_type]["count"] += 1
            by_type[r.case_type]["hours"] += r.estimated_minutes / 60
            cat_short = r.final_category.split(".")[-1] if "." in r.final_category else r.final_category
            by_category[cat_short]["count"] += 1
            by_category[cat_short]["hours"] += r.estimated_minutes / 60
            if r.area:
                by_area[r.area]["count"] += 1
                by_area[r.area]["hours"] += r.estimated_minutes / 60
            else:
                by_area["Sin área"]["count"] += 1
                by_area["Sin área"]["hours"] += r.estimated_minutes / 60

        summary = ProcessingSummary(
            total_hours=round(total_hours, 2),
            avg_minutes=round(avg_minutes, 2),
            by_type=dict(by_type),
            by_category=dict(by_category),
            by_area=dict(by_area),
        )

        return ProcessResponsibleResponse(
            processing_id=processing_id,
            responsible_name=request.responsible_name,
            total_cases=len(cases),
            cases_in_catalog=len(processable_cases),
            processed=results_count,
            rejected=rejected,
            results=results,
            results_by_area=_group_results_by_area(results),
            summary=summary,
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail={"error": "INTERNAL_ERROR", "message": f"Error: {str(e)}"})


# ============================================================================
# CATALOG ENDPOINT
# ============================================================================


@router.post(
    "/catalog/load",
    summary="Cargar catálogo de tiempos desde Excel",
    description="Carga las categorías del catálogo de tiempos desde el archivo Excel, leyendo las hojas Requerimientos e Incidentes.",
)
async def load_catalog(db: Session = Depends(get_db)):
    """Carga el catálogo de tiempos desde Excel a PostgreSQL."""
    import os
    import unicodedata

    import pandas as pd

    from ...infrastructure.database.models.catalogo_tiempos import CatalogoTiempoModel

    file_path = r"C:\Bot-Comproject\test_data\catalogo_tiempos.xlsx"

    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail={"error": "FILE_NOT_FOUND", "message": f"No se encontró {file_path}"})

    def normalize_path(s):
        s = s.lower().strip()
        s = unicodedata.normalize("NFD", s)
        s = "".join(c for c in s if unicodedata.category(c) != "Mn")
        s = s.replace("  ", " ")
        s = s.replace("infrastructura", "infraestructura")
        return s

    def normalize_type(s):
        s = s.strip().lower()
        if "incidente" in s:
            return "Incidente"
        return "Requerimiento"

    try:
        excel_file = pd.ExcelFile(file_path)
        sheet_names = excel_file.sheet_names
    except Exception as e:
        raise HTTPException(status_code=500, detail={"error": "EXCEL_READ_ERROR", "message": f"Error al leer el Excel: {str(e)}"})

    db.query(CatalogoTiempoModel).delete()
    count = 0
    loaded_sheets = []

    for sheet_name in sheet_names:
        case_type = normalize_type(sheet_name)
        df = pd.read_excel(excel_file, sheet_name=sheet_name, header=0)
        df.columns = ["idx", "Categoria", "Subcategoria", "Item", "TiempoMin", "TiempoMax"]
        df = df.iloc[1:]
        df = df.dropna(subset=["TiempoMin", "TiempoMax"])

        last_cat = None
        last_sub = None

        for _, row in df.iterrows():
            cat = str(row["Categoria"]).strip() if pd.notna(row["Categoria"]) else last_cat
            sub = str(row["Subcategoria"]).strip() if pd.notna(row["Subcategoria"]) else last_sub
            item = str(row["Item"]).strip() if pd.notna(row["Item"]) else None
            if pd.notna(row["Categoria"]):
                last_cat = cat
            if pd.notna(row["Subcategoria"]):
                last_sub = sub

            parts = [p for p in [cat, sub, item] if p]
            path_completo = ".".join(parts)
            path_normalizado = normalize_path(path_completo)

            record = CatalogoTiempoModel(
                case_type=case_type,
                nivel1=cat,
                nivel2=sub,
                nivel3=item,
                path_completo=path_completo,
                path_normalizado=path_normalizado,
                tiempo_min=int(row["TiempoMin"]),
                tiempo_max=int(row["TiempoMax"]),
            )
            db.add(record)
            count += 1

        loaded_sheets.append(f"{sheet_name} ({len(df)} categorías)")

    db.commit()

    return {
        "message": f"Catálogo cargado: {count} categorías",
        "total": count,
        "sheets": loaded_sheets,
    }


@router.get(
    "/catalog",
    response_model=CatalogResponse,
    summary="Obtener catálogo de tiempos",
    description="Retorna el catálogo de tiempos cargado en la base de datos.",
)
async def get_catalog(db: Session = Depends(get_db)):
    """
    Retorna el catálogo de tiempos.

    Returns:
        Lista de categorías con sus tiempos
    """
    try:
        catalog_repo = SQLAlchemyCatalogoTiempoRepository(db)
        all_categories = catalog_repo.get_all()

        categories = []
        for cat in all_categories:
            categories.append(
                CatalogCategory(
                    path=cat.path_completo,
                    nivel1=cat.nivel1,
                    nivel2=cat.nivel2,
                    nivel3=cat.nivel3,
                    tiempo_min=cat.tiempo_min,
                    tiempo_max=cat.tiempo_max,
                )
            )

        return CatalogResponse(
            total_categories=len(categories),
            categories=categories,
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "error": "INTERNAL_ERROR",
                "message": f"Error al obtener catálogo: {str(e)}",
            }
        )


# ============================================================================
# RESULTS ENDPOINT
# ============================================================================


@router.get(
    "/results/{processing_id}",
    response_model=GetResultsResponse,
    summary="Obtener resultados de procesamiento",
    description=(
        "Retorna los resultados guardados de un procesamiento específico. "
        "Opcionalmente filtra por rango de fechas (fecha_inicio/fecha_fin) aplicado "
        "sobre fecha_solucion del caso, y retorna las semanas disponibles para seleccionar."
    ),
)
async def get_results(
    processing_id: uuid.UUID,
    fecha_inicio: Optional[str] = Query(
        None,
        description="Inicio del rango (YYYY-MM-DD). Filtra por fecha_solucion del caso.",
    ),
    fecha_fin: Optional[str] = Query(
        None,
        description="Fin del rango (YYYY-MM-DD). Filtra por fecha_solucion del caso.",
    ),
    db: Session = Depends(get_db),
):
    """
    Retorna los resultados de un procesamiento.

    Args:
        processing_id: ID del procesamiento
        fecha_inicio: Fecha de inicio del rango (inclusive)
        fecha_fin: Fecha de fin del rango (inclusive)

    Returns:
        Resultados y resumen
    """
    try:
        # Verificar que el processing existe
        processing = db.query(ProcessingModel).filter(ProcessingModel.id == processing_id).first()
        if not processing:
            raise HTTPException(
                status_code=404,
                detail={
                    "error": "PROCESSING_NOT_FOUND",
                    "message": "No se encontró el procesamiento",
                },
            )

        # Obtener resultados
        ai_result_repo = SQLAlchemyAIResultRepository(db)
        db_results = ai_result_repo.find_by_processing(processing_id)

        # Validar/parsear rango de fechas
        range_start = None
        range_end = None
        if fecha_inicio:
            try:
                range_start = datetime.strptime(fecha_inicio, "%Y-%m-%d").date()
            except ValueError:
                raise HTTPException(
                    status_code=422,
                    detail={
                        "error": "INVALID_DATE",
                        "message": "fecha_inicio debe tener formato YYYY-MM-DD",
                    },
                )
        if fecha_fin:
            try:
                range_end = datetime.strptime(fecha_fin, "%Y-%m-%d").date()
            except ValueError:
                raise HTTPException(
                    status_code=422,
                    detail={
                        "error": "INVALID_DATE",
                        "message": "fecha_fin debe tener formato YYYY-MM-DD",
                    },
                )
        if range_start and range_end and range_start > range_end:
            raise HTTPException(
                status_code=422,
                detail={
                    "error": "INVALID_RANGE",
                    "message": "fecha_inicio no puede ser mayor que fecha_fin",
                },
            )

        all_results = []
        catalog_repo = SQLAlchemyCatalogoTiempoRepository(db)
        for r in db_results:
            catalog_item = (r.final_category or "").split(".")[-1]
            if r.case and r.case.final_category:
                matched = catalog_repo.find_by_path(r.case.final_category, r.case.case_type)
                if matched:
                    catalog_item = matched.nivel3 or matched.path_completo.split(".")[-1]
            all_results.append(
                AIResultResponse(
                    case_code=r.case_code,
                    final_category=r.final_category or "",
                    catalog_category=catalog_item,
                    status=r.status or "",
                    case_type=r.case_type or "",
                    cliente=r.case.user_name if r.case else None,
                    area=r.case.area if r.case else None,
                    fecha_solucion=_format_fecha(r.case.fecha_solucion) if r.case else None,
                    original_description=r.case.description if r.case else None,
                    solution=r.case.solution if r.case else None,
                    generated_description=r.generated_description,
                    estimated_minutes=r.estimated_minutes,
                    model_name=r.model_name,
                    tokens_used=r.tokens_used or 0,
                    latency_ms=r.latency_ms or 0.0,
                )
            )

        # Semanas disponibles (derivadas de fecha_solucion)
        def _week_key(fecha):
            """Retorna (inicio_lunes, fin_domingo) para una fecha."""
            iso = fecha.isocalendar()
            monday = datetime.fromisocalendar(iso.year, iso.week, 1).date()
            sunday = monday + timedelta(days=6)
            return monday, sunday

        from collections import defaultdict
        from datetime import date as _date, timedelta

        weeks = defaultdict(lambda: {"count": 0, "total_minutes": 0})
        for r in all_results:
            if r.fecha_solucion:
                try:
                    fecha = _date.fromisoformat(r.fecha_solucion)
                    monday, sunday = _week_key(fecha)
                    key = f"{monday.isoformat()}|{sunday.isoformat()}"
                    weeks[key]["count"] += 1
                    weeks[key]["total_minutes"] += r.estimated_minutes
                except ValueError:
                    continue

        semanas_disponibles = [
            WeekInfo(
                fecha_inicio=iso_fecha.split("|")[0],
                fecha_fin=iso_fecha.split("|")[1],
                count=info["count"],
                total_hours=round(info["total_minutes"] / 60, 2),
            )
            for iso_fecha, info in sorted(weeks.items(), key=lambda x: x[0])
        ]

        # Aplicar filtro por rango de fechas
        results = all_results
        if range_start or range_end:
            filtered = []
            for r in all_results:
                if not r.fecha_solucion:
                    continue
                try:
                    fecha = _date.fromisoformat(r.fecha_solucion)
                except ValueError:
                    continue
                if range_start and fecha < range_start:
                    continue
                if range_end and fecha > range_end:
                    continue
                filtered.append(r)
            results = filtered

        # Calcular resumen
        total_minutes = sum(r.estimated_minutes for r in results)
        total_hours = total_minutes / 60
        avg_minutes = total_minutes / len(results) if results else 0

        from collections import defaultdict
        by_type = defaultdict(lambda: {"count": 0, "hours": 0})
        by_category = defaultdict(lambda: {"count": 0, "hours": 0})
        by_area = defaultdict(lambda: {"count": 0, "hours": 0})
        for r in results:
            if r.case_type:
                by_type[r.case_type]["count"] += 1
                by_type[r.case_type]["hours"] += r.estimated_minutes / 60
            if r.final_category:
                cat_short = r.final_category.split(".")[-1] if "." in r.final_category else r.final_category
                by_category[cat_short]["count"] += 1
                by_category[cat_short]["hours"] += r.estimated_minutes / 60
            if r.area:
                by_area[r.area]["count"] += 1
                by_area[r.area]["hours"] += r.estimated_minutes / 60
            else:
                by_area["Sin área"]["count"] += 1
                by_area["Sin área"]["hours"] += r.estimated_minutes / 60

        summary = ProcessingSummary(
            total_hours=round(total_hours, 2),
            avg_minutes=round(avg_minutes, 2),
            by_type=dict(by_type),
            by_category=dict(by_category),
            by_area=dict(by_area),
        )

        return GetResultsResponse(
            processing_id=processing_id,
            responsible_name=processing.responsible_name or "",
            total_results=len(results),
            total_results_all=len(all_results),
            fecha_inicio=fecha_inicio,
            fecha_fin=fecha_fin,
            semanas_disponibles=semanas_disponibles,
            results=results,
            results_by_area=_group_results_by_area(results),
            summary=summary,
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "error": "INTERNAL_ERROR",
                "message": f"Error al obtener resultados: {str(e)}",
            }
        )


# ============================================================================
# SINGLE CASE ENDPOINTS (EXISTING)
# ============================================================================


class DescriptionRequest(BaseModel):
    """Schema de entrada para generación de descripción."""
    case_code: str = Field(..., description="Código del caso")
    case_type: str = Field(..., description="Tipo de caso")
    final_category: str = Field(..., description="Categoría del caso")
    description: str = Field(..., description="Descripción original")
    solution: Optional[str] = Field(None, description="Solución del caso")


class DescriptionResponse(BaseModel):
    """Schema de respuesta para descripción generada."""
    case_code: str
    generated_description: str
    is_valid: bool
    starts_with_se_realizo: bool
    length: int


class EstimationRequest(BaseModel):
    """Schema de entrada para estimación de tiempo."""
    case_code: str = Field(..., description="Código del caso")
    case_type: str = Field(..., description="Tipo de caso")
    final_category: str = Field(..., description="Categoría del caso")
    description: str = Field(..., description="Descripción del caso")


class EstimationResponse(BaseModel):
    """Schema de respuesta para estimación de tiempo."""
    case_code: str
    estimated_minutes: int
    is_valid: bool
    in_range: bool


class HealthResponse(BaseModel):
    """Schema de respuesta para health check de IA."""
    status: str
    model: str
    available: bool


@router.post(
    "/generate-description",
    response_model=DescriptionResponse,
    summary="Generar descripción con IA",
    description="Genera una descripción breve y formal para un caso usando IA.",
)
async def generate_description(request: DescriptionRequest):
    """
    Genera una descripción breve para un caso.

    Args:
        request: Datos del caso

    Returns:
        Descripción generada validada
    """
    try:
        provider = OllamaProvider(base_url=settings.ollama.base_url)
        ai_service = AIService(ai_provider=provider)

        if not await ai_service.health_check():
            raise HTTPException(
                status_code=503,
                detail={
                    "error": "AI_SERVICE_UNAVAILABLE",
                    "message": "El servicio de IA no está disponible",
                },
            )

        case = {
            "case_code": request.case_code,
            "case_type": request.case_type,
            "final_category": request.final_category,
            "description": request.description,
            "solution": request.solution or "",
        }

        response = await ai_service.generate_description(case)

        if not response.success:
            raise HTTPException(
                status_code=500,
                detail={
                    "error": "AI_GENERATION_FAILED",
                    "message": response.error or "Error al generar descripción",
                },
            )

        parsed = parser.parse_description(response.content)

        return DescriptionResponse(
            case_code=request.case_code,
            generated_description=parsed.text,
            is_valid=parsed.is_valid,
            starts_with_se_realizo=parsed.starts_with_se_realizo,
            length=parsed.length,
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "error": "INTERNAL_ERROR",
                "message": f"Error al generar descripción: {str(e)}",
            }
        )


@router.post(
    "/estimate-time",
    response_model=EstimationResponse,
    summary="Estimar tiempo con IA",
    description="Estima el tiempo de resolución para un caso usando IA.",
)
async def estimate_time(request: EstimationRequest):
    """
    Estima el tiempo de resolución para un caso.

    Args:
        request: Datos del caso

    Returns:
        Estimación de tiempo validada
    """
    try:
        provider = OllamaProvider(base_url=settings.ollama.base_url)
        ai_service = AIService(ai_provider=provider)

        if not await ai_service.health_check():
            raise HTTPException(
                status_code=503,
                detail={
                    "error": "AI_SERVICE_UNAVAILABLE",
                    "message": "El servicio de IA no está disponible",
                },
            )

        case = {
            "case_code": request.case_code,
            "case_type": request.case_type,
            "final_category": request.final_category,
            "description": request.description,
        }

        response = await ai_service.estimate_time(case)

        if not response.success:
            raise HTTPException(
                status_code=500,
                detail={
                    "error": "AI_ESTIMATION_FAILED",
                    "message": response.error or "Error al estimar tiempo",
                },
            )

        parsed = parser.parse_estimation(response.content)

        return EstimationResponse(
            case_code=request.case_code,
            estimated_minutes=parsed.minutes,
            is_valid=parsed.is_valid,
            in_range=parsed.in_range,
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "error": "INTERNAL_ERROR",
                "message": f"Error al estimar tiempo: {str(e)}",
            }
        )


@router.get(
    "/health",
    response_model=HealthResponse,
    summary="Verificar salud del servicio de IA",
    description="Verifica que el servicio de IA esté disponible y funcionando.",
)
async def ai_health_check():
    """
    Verifica la salud del servicio de IA.

    Returns:
        Estado del servicio de IA
    """
    try:
        config = AIConfig(model=settings.ollama.model, timeout=settings.ollama.timeout)
        provider = OllamaProvider(base_url=settings.ollama.base_url)
        ai_service = AIService(ai_provider=provider, config=config)

        is_healthy = await ai_service.health_check()

        return HealthResponse(
            status="healthy" if is_healthy else "unhealthy",
            model=ai_service.config.model,
            available=is_healthy,
        )

    except Exception as e:
        return HealthResponse(
            status="error",
            model="unknown",
            available=False,
        )


class TestProcessRequest(BaseModel):
    upload_id: str
    responsible_name: str
    max_cases: int = 5


class TestProcessResponse(BaseModel):
    results: list
    total_processed: int


@router.post(
    "/test-process",
    response_model=TestProcessResponse,
    summary="Probar procesamiento IA sin guardar en BD",
    description="Procesa casos con IA y devuelve resultados sin guardar en base de datos.",
)
def test_process_ai(
    request: TestProcessRequest,
    db: Session = Depends(get_db),
):
    """Procesa casos con IA sin guardar resultados."""
    import httpx
    from ...infrastructure.ai.response_parser import ResponseParser

    catalog_repo = SQLAlchemyCatalogoTiempoRepository(db)
    all_catalog_paths = catalog_repo.get_all_paths()

    if not all_catalog_paths:
        raise HTTPException(status_code=404, detail={"error": "CATALOG_EMPTY"})

    cases = (
        db.query(CaseModel)
        .filter(
            CaseModel.upload_id == request.upload_id,
            CaseModel.responsible_name == request.responsible_name,
            CaseModel.case_type.in_(["Incidente", "Requerimiento"]),
            CaseModel.status.in_(PROCESSABLE_STATUSES),
        )
        .limit(request.max_cases)
        .all()
    )

    if not cases:
        raise HTTPException(status_code=404, detail={"error": "NO_CASES_FOUND"})

    processable_cases = [c for c in cases if catalog_repo.find_by_path(c.final_category, c.case_type)]

    if not processable_cases:
        raise HTTPException(status_code=404, detail={"error": "NO_CASES_IN_CATALOG"})

    config = AIConfig(model=settings.ollama.model, timeout=settings.ollama.timeout)
    provider = OllamaProvider(base_url=settings.ollama.base_url)
    ai_service = AIService(ai_provider=provider, config=config)
    parser = ResponseParser()

    results = []

    for case in processable_cases:
        try:
            time_range = catalog_repo.get_time_range(case.final_category, case.case_type)
            estimated_minutes = (time_range["min"] + time_range["max"]) // 2

            case_data = {
                "case_code": case.case_code,
                "case_type": case.case_type,
                "final_category": case.final_category,
                "description": case.description,
                "solution": case.solution or "",
            }

            prompt = ai_service._build_description_context(case_data)
            start_time = time.time()

            with httpx.Client(timeout=config.timeout) as client:
                response = client.post(
                    f"{provider.base_url}/api/generate",
                    json={
                        "model": config.model,
                        "prompt": prompt,
                        "stream": False,
                        "options": {"temperature": config.temperature, "num_predict": config.max_tokens},
                    },
                )
                response.raise_for_status()
                data = response.json()
                latency_ms = (time.time() - start_time) * 1000
                ai_content = data.get("response", "")
                tokens_used = data.get("eval_count", 0)

            if ai_content:
                parsed = parser.parse_description(ai_content)
                generated_description = parsed.text
            else:
                generated_description = "Sin descripción generada"

            results.append({
                "case_code": case.case_code,
                "case_type": case.case_type,
                "cliente": case.user_name,
                "final_category": case.final_category,
                "original_description": case.description,
                "solution": case.solution,
                "generated_description": generated_description,
                "estimated_minutes": estimated_minutes,
                "time_range": f"{time_range['min']}-{time_range['max']} min",
                "latency_ms": round(latency_ms, 2),
                "tokens_used": tokens_used,
            })

        except Exception as e:
            results.append({
                "case_code": case.case_code,
                "final_category": case.final_category,
                "error": str(e),
            })

    return TestProcessResponse(results=results, total_processed=len(results))
