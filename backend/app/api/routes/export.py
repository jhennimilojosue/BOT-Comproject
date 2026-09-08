"""
Export Routes - Endpoints para exportación de resultados.

Responsabilidades:
- Exportar resultados de procesamiento a Excel
- Generar archivos .xlsx con los datos procesados
"""

import io
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from ...infrastructure.database.models.case import CaseModel
from ...infrastructure.database.models.processing import ProcessingModel
from ...infrastructure.database.models.ai_result import AIResultModel
from ..dependencies import get_db

router = APIRouter(prefix="/api/v1/processing", tags=["processing"])


@router.get(
    "/{processing_id}/export",
    summary="Exportar resultados a Excel",
    description="Genera un archivo Excel con los resultados del procesamiento.",
)
async def export_processing_results(
    processing_id: UUID,
    db: Session = Depends(get_db),
):
    """
    Exporta los resultados de un procesamiento a un archivo Excel.

    Args:
        processing_id: Identificador del procesamiento
        db: Sesión de base de datos

    Returns:
        Archivo Excel con los resultados
    """
    try:
        # Verificar que el procesamiento existe
        processing = db.query(ProcessingModel).filter(
            ProcessingModel.id == processing_id
        ).first()

        if not processing:
            raise HTTPException(
                status_code=404,
                detail={
                    "error": "PROCESSING_NOT_FOUND",
                    "message": f"No se encontró el procesamiento {processing_id}",
                },
            )

        # Obtener los casos del upload
        cases = db.query(CaseModel).filter(
            CaseModel.upload_id == processing.upload_id
        ).all()

        # Obtener resultados IA asociados al procesamiento
        ai_results = db.query(AIResultModel).filter(
            AIResultModel.processing_id == processing_id
        ).all()
        ai_by_case = {r.case_code: r for r in ai_results}

        # Crear el archivo Excel en memoria
        output = io.BytesIO()

        try:
            import openpyxl
            from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
            
            workbook = openpyxl.Workbook()
            sheet = workbook.active
            sheet.title = "Resultados"

            # Estilos para el encabezado
            header_font = Font(bold=True, color="FFFFFF")
            header_fill = PatternFill(start_color="4472C4", end_color="4472C4", fill_type="solid")
            header_alignment = Alignment(horizontal="center", vertical="center")
            thin_border = Border(
                left=Side(style="thin"),
                right=Side(style="thin"),
                top=Side(style="thin"),
                bottom=Side(style="thin"),
            )

            # Encabezados
            headers = [
                "Código",
                "Tipo",
                "Responsable",
                "Estado",
                "Categoría",
                "Fecha Registro",
                "Descripción",
                "Solución",
                "Descripción IA",
                "Tiempo Estimado (min)",
                "Tiempo Estimado (horas)",
            ]

            for col, header in enumerate(headers, 1):
                cell = sheet.cell(row=1, column=col, value=header)
                cell.font = header_font
                cell.fill = header_fill
                cell.alignment = header_alignment
                cell.border = thin_border

            # Datos
            for row, case in enumerate(cases, 2):
                ai = ai_by_case.get(case.case_code)
                estimated_minutes = ai.estimated_minutes if ai else None
                estimated_hours = round(estimated_minutes / 60, 2) if estimated_minutes is not None else None

                registered_at = case.registered_at
                if registered_at is not None and registered_at.tzinfo is not None:
                    registered_at = registered_at.replace(tzinfo=None)

                values = [
                    case.case_code,
                    case.case_type,
                    case.responsible_name,
                    case.status,
                    case.final_category,
                    registered_at,
                    case.description,
                    case.solution,
                    ai.generated_description if ai else None,
                    estimated_minutes,
                    estimated_hours,
                ]
                for col, value in enumerate(values, 1):
                    sheet.cell(row=row, column=col, value=value).border = thin_border

            # Ajustar ancho de columnas
            for col in range(1, len(headers) + 1):
                sheet.column_dimensions[openpyxl.utils.get_column_letter(col)].width = 30

            # Guardar en memoria
            workbook.save(output)
            output.seek(0)

        except ImportError:
            raise HTTPException(
                status_code=500,
                detail={
                    "error": "MISSING_DEPENDENCY",
                    "message": "openpyxl no está instalado. Ejecute: pip install openpyxl",
                },
            )

        # Retornar como archivo Excel
        filename = f"resultados_{processing_id}.xlsx"
        return StreamingResponse(
            output,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={
                "Content-Disposition": f"attachment; filename={filename}"
            },
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "error": "INTERNAL_ERROR",
                "message": f"Error al exportar resultados: {str(e)}",
            },
        )
