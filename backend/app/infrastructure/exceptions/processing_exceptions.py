"""
Processing Exceptions - Excepciones del módulo de procesamiento.
"""


class ProcessingException(Exception):
    """Excepción base para errores de procesamiento."""

    def __init__(self, message: str, error_code: str = "PROCESSING_ERROR"):
        self.message = message
        self.error_code = error_code
        super().__init__(self.message)


class StatusNotProcessableException(ProcessingException):
    """Excepción para estados no procesables."""

    def __init__(self, status: str):
        self.status = status
        message = f"Estado '{status}' no es procesable"
        super().__init__(message, "STATUS_NOT_PROCESSABLE")


class CategoryNotConfiguredException(ProcessingException):
    """Excepción para categorías no configuradas."""

    def __init__(self, case_type: str, category: str):
        self.case_type = case_type
        self.category = category
        message = f"Categoría '{category}' no configurada para tipo '{case_type}'"
        super().__init__(message, "CATEGORY_NOT_CONFIGURED")


class ResponsibleNotFoundException(ProcessingException):
    """Excepción para responsables no encontrados."""

    def __init__(self, responsible_id: str = None, responsible_name: str = None):
        self.responsible_id = responsible_id
        self.responsible_name = responsible_name
        if responsible_id:
            message = f"Responsable con ID '{responsible_id}' no encontrado"
        else:
            message = f"Responsable '{responsible_name}' no encontrado"
        super().__init__(message, "RESPONSIBLE_NOT_FOUND")
