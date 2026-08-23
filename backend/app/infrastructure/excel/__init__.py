"""
Paquete de infraestructura Excel.

Este paquete contiene los componentes del Excel Service:
- FileValidator: Validación de archivos
- StructureValidator: Validación de estructura
- HeaderResolver: Resolución de cabeceras
- ColumnMapper: Mapeo de columnas
- DataExtractor: Extracción de datos
- DataNormalizer: Normalización de datos
- CaseMapper: Mapeo a Case
- ExcelService: Orquestador del pipeline
"""

from .file_validator import (
    FileValidator,
    validate_excel_file,
)
from .structure_validator import (
    StructureValidator,
    validate_excel_structure,
)
from .header_resolver import (
    HeaderResolver,
    resolve_excel_headers,
)
from .column_mapper import (
    ColumnMapper,
    map_excel_columns,
)
from .data_extractor import (
    DataExtractor,
    extract_excel_data,
)
from .data_normalizer import (
    DataNormalizer,
    normalize_excel_data,
)
from .case_mapper import (
    CaseMapper,
    ExcelCaseDTO,
    map_to_excel_cases,
)
from .excel_service import ExcelService

__all__ = [
    "FileValidator",
    "validate_excel_file",
    "StructureValidator",
    "validate_excel_structure",
    "HeaderResolver",
    "resolve_excel_headers",
    "ColumnMapper",
    "map_excel_columns",
    "DataExtractor",
    "extract_excel_data",
    "DataNormalizer",
    "normalize_excel_data",
    "CaseMapper",
    "ExcelCaseDTO",
    "map_to_excel_cases",
    "ExcelService",
]
