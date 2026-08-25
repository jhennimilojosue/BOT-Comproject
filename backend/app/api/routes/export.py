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
            ]

            for col, header in enumerate(headers, 1):
                cell = sheet.cell(row=1, column=col, value=header)
                cell.font = header_font
                cell.fill = header_fill
                cell.alignment = header_alignment
                cell.border = thin_border

            # Datos
            for row, case in enumerate(cases, 2):
                sheet.cell(row=row, column=1, value=case.case_code).border = thin_border
                sheet.cell(row=row, column=2, value=case.case_type).border = thin_border
                sheet.cell(row=row, column=3, value=case.responsible_name).border = thin_border
                sheet.cell(row=row, column=4, value=case.status).border = thin_border
                sheet.cell(row=row, column=5, value=case.final_category).border = thin_border
                sheet.cell(row=row, column=6, value=case.registered_at).border = thin_border
                sheet.cell(row=row, column=7, value=case.description).border = thin_border
                sheet.cell(row=row, column=8, value=case.solution).border = thin_border

            # Ajustar ancho de columnas
            for col in range(1, 9):
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
