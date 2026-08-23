"""
Excel Service - Orquestador del procesamiento del Maestro de Casos.

Responsabilidades (procesamiento_maestro.md):
- Recibir archivos .xlsx
- Validar archivo y estructura
- Identificar encabezados
- Mapear columnas
- Extraer y normalizar datos
- Entregar List[ExcelCaseDTO] a Gestión de Casos

Este servicio NO aplica reglas de negocio de procesabilidad,
no consulta catálogos, no usa IA y no accede a PostgreSQL.
"""

import io
from typing import List

import pandas as pd
from fastapi import UploadFile

from .case_mapper import CaseMapper, ExcelCaseDTO
from .column_mapper import ColumnMapper
from .data_extractor import DataExtractor
from .data_normalizer import DataNormalizer
from .file_validator import FileValidator
from .header_resolver import HeaderResolver
from .structure_validator import StructureValidator


class ExcelService:
    """
    Orquesta el flujo completo de transformación del Maestro de Casos.

    Flujo interno (sección 19 de procesamiento_maestro.md):

    ```
    Archivo Excel
         │
         ▼
    File Validation          (FileValidator)
         │
         ▼
    Lectura técnica (.xlsx)  (pandas)
         │
         ▼
    Header Resolver          (HeaderResolver)
         │
         ▼
    Structure Validator      (StructureValidator)
         │
         ▼
    Column Mapper            (ColumnMapper)
         │
         ▼
    Data Extractor           (DataExtractor)
         │
         ▼
    Data Normalizer          (DataNormalizer)
         │
         ▼
    Case Mapper              (CaseMapper)
         │
         ▼
    List[ExcelCaseDTO]  ──►  Gestión de Casos
    ```
    """

    def __init__(
        self,
        file_validator: FileValidator = None,
        header_resolver: HeaderResolver = None,
        structure_validator: StructureValidator = None,
        column_mapper: ColumnMapper = None,
        data_extractor: DataExtractor = None,
        data_normalizer: DataNormalizer = None,
        case_mapper: CaseMapper = None,
    ):
        self.file_validator = file_validator or FileValidator()
        self.header_resolver = header_resolver or HeaderResolver()
        self.structure_validator = structure_validator or StructureValidator()
        self.column_mapper = column_mapper or ColumnMapper()
        self.data_extractor = data_extractor or DataExtractor()
        self.data_normalizer = data_normalizer or DataNormalizer()
        self.case_mapper = case_mapper or CaseMapper()

    def process(self, file: UploadFile) -> List[ExcelCaseDTO]:
        """
        Procesa el Maestro de Casos y retorna los casos extraídos.

        Args:
            file: Archivo Excel subido por el usuario

        Returns:
            Lista de ExcelCaseDTO listos para Gestión de Casos

        Raises:
            FileValidationError: Si el archivo no es válido
            UnreadableFileError: Si el archivo no puede leerse
            StructureValidationError: Si la estructura no es la esperada
            InvalidDataFormatError: Si un dato no puede convertirse
            ValidationError: Si un registro no cumple el Case Contract
        """
        self.file_validator.validate(file)

        raw_df = self._read_excel(file)
        resolved_df = self.header_resolver.resolve(raw_df)
        self.structure_validator.validate(resolved_df)

        mapped_df = self.column_mapper.rename_columns(resolved_df)
        records = self.data_extractor.extract(mapped_df)
        normalized_records = self.data_normalizer.normalize(records)

        return self.case_mapper.map(normalized_records)

    def _read_excel(self, file: UploadFile) -> pd.DataFrame:
        """
        Lee técnicamente el archivo .xlsx sin asumir fila de encabezados.

        Args:
            file: Archivo ya validado

        Returns:
            DataFrame crudo con header=None
        """
        content = file.file.read()
        file.file.seek(0)
        return pd.read_excel(io.BytesIO(content), header=None, dtype=str)
