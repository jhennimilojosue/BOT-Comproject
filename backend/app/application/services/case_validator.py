"""
Case Validator - Componente de Gestión de Casos.

Responsabilidades (gestion_casos.md sección 9):
- Validar la estructura mínima necesaria del caso
- Verificar presencia y validez de los campos obligatorios

El Case Validator NO determina si un estado o categoría son válidos
según negocio. Estas decisiones corresponden a Catalog Service.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel


@dataclass
class ValidationErrorDetail:
    """Detalle de un error de validación estructural."""

    field: str
    code: str
    message: str


@dataclass
class ValidationResult:
    """Resultado de la validación estructural de un Case."""

    valid: bool = True
    errors: List[ValidationErrorDetail] = field(default_factory=list)


class CaseValidator:
    """
    Valida que el Case cumpla el contrato antes de continuar con el procesamiento.

    Campos obligatorios (Case Contract v1.2):
    case_code, responsible_name, project, registered_at,
    status, final_category, description, solution

    Campo opcional:
    user_name
    """

    REQUIRED_TEXT_FIELDS = [
        "case_code",
        "responsible_name",
        "project",
        "status",
        "final_category",
        "description",
        "solution",
    ]

    DATE_FIELD = "registered_at"
    OPTIONAL_FIELDS = ["user_name"]

    def validate(self, case: BaseModel) -> ValidationResult:
        """
        Valida un caso individual.

        Args:
            case: DTO del caso compatible con el Case Contract

        Returns:
            ValidationResult con el detalle de errores si los hay
        """
        data = case.model_dump()
        errors: List[ValidationErrorDetail] = []

        errors.extend(self._validate_required_fields(data))
        date_error = self._validate_date(data.get(self.DATE_FIELD))
        if date_error:
            errors.append(date_error)

        return ValidationResult(valid=len(errors) == 0, errors=errors)

    def _validate_required_fields(
        self, data: dict
    ) -> List[ValidationErrorDetail]:
        """
        Verifica que los campos obligatorios existan y no estén vacíos.

        Args:
            data: Datos del caso

        Returns:
            Lista de errores encontrados
        """
        errors = []

        for name in self.REQUIRED_TEXT_FIELDS:
            value = data.get(name)
            if self._is_empty(value):
                errors.append(
                    ValidationErrorDetail(
                        field=name,
                        code="REQUIRED_FIELD_MISSING",
                        message=f"El campo obligatorio '{name}' está vacío o ausente.",
                    )
                )

        return errors

    def _validate_date(self, value) -> Optional[ValidationErrorDetail]:
        """
        Verifica que la fecha sea válida y esté en formato ISO.

        Args:
            value: Valor del campo fecha

        Returns:
            Error si la fecha es inválida, None en caso contrario
        """
        if self._is_empty(value):
            return ValidationErrorDetail(
                field=self.DATE_FIELD,
                code="REQUIRED_FIELD_MISSING",
                message=f"El campo obligatorio '{self.DATE_FIELD}' está vacío o ausente.",
            )

        try:
            datetime.strptime(str(value), "%Y-%m-%d")
        except ValueError:
            return ValidationErrorDetail(
                field=self.DATE_FIELD,
                code="INVALID_DATE_FORMAT",
                message=(
                    f"El campo '{self.DATE_FIELD}' debe tener "
                    f"formato YYYY-MM-DD. Valor recibido: '{value}'."
                ),
            )

        return None

    def _is_empty(self, value) -> bool:
        """Determina si un valor está ausente o vacío."""
        return value is None or str(value).strip() == ""
