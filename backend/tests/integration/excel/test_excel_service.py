"""
Tests de integración para el Excel Service.

Validan el flujo completo con archivos .xlsx reales:
FileValidator → HeaderResolver → StructureValidator → ColumnMapper
→ DataExtractor → DataNormalizer → CaseMapper
"""

import io

import pytest
from fastapi import UploadFile
from openpyxl import Workbook

from app.infrastructure.exceptions.excel_exceptions import (
    FileValidationError,
    StructureValidationError,
)
from app.infrastructure.excel.excel_service import ExcelService

REQUIRED_COLUMNS = [
    "Codigo Caso",
    "Responsible Name",
    "Proyecto",
    "Fecha",
    "Estado",
    "Categoria",
    "Descripcion",
    "Solucion",
]


def build_workbook(
    rows_before_header: int = 0, include_user_column: bool = False
) -> Workbook:
    """Construye un Workbook del Maestro de Casos para pruebas."""
    wb = Workbook()
    ws = wb.active

    for i in range(rows_before_header):
        ws.append([f"Fila decorativa {i + 1}"])

    headers = REQUIRED_COLUMNS.copy()
    if include_user_column:
        headers.append("Usuario")
    ws.append(headers)

    row = [
        "INC001245", "Carlos Rodríguez", "Hospital Militar",
        "10/08/2026", "Solucionado", "Ingreso de Huella",
        "Problema con el registro de huella.",
        "Se realizó la configuración correspondiente.",
    ]
    if include_user_column:
        row.append("  Juan Pérez  ")
    ws.append(row)

    return wb


def build_upload_file(wb: Workbook, filename: str = "maestro_casos.xlsx") -> UploadFile:
    """Convierte un Workbook en UploadFile."""
    buffer = io.BytesIO()
    wb.save(buffer)
    buffer.seek(0)
    return UploadFile(filename=filename, file=buffer)


class TestExcelServiceIntegration:
    """Tests de integración del flujo completo del Excel Service."""

    def setup_method(self):
        """Configuración inicial para cada test."""
        self.service = ExcelService()

    def test_should_process_valid_file_with_header_in_first_row(self):
        """Test: Debe procesar un archivo válido con encabezados en la primera fila."""
        # Arrange
        file = build_upload_file(build_workbook())

        # Act
        cases = self.service.process(file)

        # Assert
        assert len(cases) == 1
        case = cases[0]
        assert case.case_code == "INC001245"
        assert case.responsible_name == "Carlos Rodríguez"
        assert case.project == "Hospital Militar"
        assert case.registered_at == "2026-08-10"
        assert case.status == "Solucionado"
        assert case.final_category == "Ingreso de Huella"
        assert case.user_name is None

    def test_should_process_file_with_decorative_rows_before_header(self):
        """Test: Debe procesar archivos con filas decorativas antes del encabezado."""
        # Arrange
        file = build_upload_file(build_workbook(rows_before_header=3))

        # Act
        cases = self.service.process(file)

        # Assert
        assert len(cases) == 1
        assert cases[0].case_code == "INC001245"

    def test_should_normalize_optional_user_field(self):
        """Test: Debe normalizar el campo opcional Usuario (espacios)."""
        # Arrange
        file = build_upload_file(build_workbook(include_user_column=True))

        # Act
        cases = self.service.process(file)

        # Assert
        assert cases[0].user_name == "Juan Pérez"

    def test_should_reject_non_xlsx_file(self):
        """Test: Debe rechazar archivos que no sean .xlsx."""
        # Arrange
        file = UploadFile(
            filename="maestro.csv",
            file=io.BytesIO(b"codigo,responsable\nINC001,Carlos"),
        )

        # Act & Assert
        with pytest.raises(FileValidationError):
            self.service.process(file)

    def test_should_reject_empty_xlsx(self):
        """Test: Debe rechazar un archivo .xlsx sin contenido estructural."""
        # Arrange
        wb = Workbook()
        wb.active.append(["Solo texto suelto"])
        file = build_upload_file(wb)

        # Act & Assert
        with pytest.raises(StructureValidationError):
            self.service.process(file)

    def test_should_reject_file_missing_required_column(self):
        """Test: Debe rechazar archivo al que le falta una columna obligatoria."""
        # Arrange
        wb = Workbook()
        incomplete_headers = REQUIRED_COLUMNS[:-1]  # Sin "Solucion"
        wb.active.append(incomplete_headers)
        file = build_upload_file(wb)

        # Act & Assert
        with pytest.raises(StructureValidationError):
            self.service.process(file)
