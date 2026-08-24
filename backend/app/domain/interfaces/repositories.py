"""
Repository Interfaces - Interfaces para repositorios de persistencia.

Responsabilidades:
- Definir contratos para acceso a datos
- Establecer operaciones CRUD para cada entidad
- Mantener separación entre dominio e infraestructura

Estas interfaces son utilizadas por la capa de dominio.
Las implementaciones concretas estarán en infrastructure.
"""

from abc import ABC, abstractmethod
from typing import Optional
from uuid import UUID

from ..entities.case import Case
from ..entities.estimation import Estimation
from ..entities.processing import Processing
from ..entities.processing_rejection import ProcessingRejection
from ..entities.upload import Upload


class UploadRepository(ABC):
    """
    Interfaz para el repositorio de Uploads.

    Define las operaciones de persistencia para la entidad Upload.
    """

    @abstractmethod
    def save(self, upload: Upload) -> None:
        """
        Guarda un upload.

        Args:
            upload: Upload a guardar
        """
        pass

    @abstractmethod
    def find_by_id(self, upload_id: UUID) -> Optional[Upload]:
        """
        Busca un upload por su ID.

        Args:
            upload_id: Identificador del upload

        Returns:
            Upload encontrado o None
        """
        pass

    @abstractmethod
    def update(self, upload: Upload) -> None:
        """
        Actualiza un upload existente.

        Args:
            upload: Upload con los datos actualizados
        """
        pass


class CaseRepository(ABC):
    """
    Interfaz para el repositorio de Cases.

    Define las operaciones de persistencia para la entidad Case.
    """

    @abstractmethod
    def save(self, case: Case) -> None:
        """
        Guarda un case.

        Args:
            case: Case a guardar
        """
        pass

    @abstractmethod
    def save_batch(self, cases: list[Case]) -> None:
        """
        Guarda múltiples cases.

        Args:
            cases: Lista de cases a guardar
        """
        pass

    @abstractmethod
    def find_by_id(self, case_id: UUID) -> Optional[Case]:
        """
        Busca un case por su ID.

        Args:
            case_id: Identificador del case

        Returns:
            Case encontrado o None
        """
        pass

    @abstractmethod
    def find_by_upload(self, upload_id: UUID) -> list[Case]:
        """
        Busca todos los cases de un upload.

        Args:
            upload_id: Identificador del upload

        Returns:
            Lista de cases encontrados
        """
        pass

    @abstractmethod
    def find_by_code_and_upload(
        self, case_code: str, upload_id: UUID
    ) -> Optional[Case]:
        """
        Busca un case por código y upload.

        Args:
            case_code: Código del caso
            upload_id: Identificador del upload

        Returns:
            Case encontrado o None
        """
        pass

    @abstractmethod
    def exists_by_code_and_upload(
        self, case_code: str, upload_id: UUID
    ) -> bool:
        """
        Verifica si existe un case por código y upload.

        Args:
            case_code: Código del caso
            upload_id: Identificador del upload

        Returns:
            True si existe
        """
        pass

    @abstractmethod
    def update(self, case: Case) -> None:
        """
        Actualiza un case existente.

        Args:
            case: Case con los datos actualizados
        """
        pass


class ProcessingRepository(ABC):
    """
    Interfaz para el repositorio de Processings.

    Define las operaciones de persistencia para la entidad Processing.
    """

    @abstractmethod
    def save(self, processing: Processing) -> None:
        """
        Guarda un processing.

        Args:
            processing: Processing a guardar
        """
        pass

    @abstractmethod
    def find_by_id(self, processing_id: UUID) -> Optional[Processing]:
        """
        Busca un processing por su ID.

        Args:
            processing_id: Identificador del processing

        Returns:
            Processing encontrado o None
        """
        pass

    @abstractmethod
    def find_by_upload(self, upload_id: UUID) -> list[Processing]:
        """
        Busca todos los processings de un upload.

        Args:
            upload_id: Identificador del upload

        Returns:
            Lista de processings encontrados
        """
        pass

    @abstractmethod
    def update(self, processing: Processing) -> None:
        """
        Actualiza un processing existente.

        Args:
            processing: Processing con los datos actualizados
        """
        pass


class ProcessingRejectionRepository(ABC):
    """
    Interfaz para el repositorio de ProcessingRejections.

    Define las operaciones de persistencia para la entidad ProcessingRejection.
    """

    @abstractmethod
    def save(self, rejection: ProcessingRejection) -> None:
        """
        Guarda un processing rejection.

        Args:
            rejection: ProcessingRejection a guardar
        """
        pass

    @abstractmethod
    def save_batch(self, rejections: list[ProcessingRejection]) -> None:
        """
        Guarda múltiples processing rejections.

        Args:
            rejections: Lista de processing rejections a guardar
        """
        pass

    @abstractmethod
    def find_by_processing(
        self, processing_id: UUID
    ) -> list[ProcessingRejection]:
        """
        Busca todos los rejections de un processing.

        Args:
            processing_id: Identificador del processing

        Returns:
            Lista de processing rejections encontrados
        """
        pass


class EstimationRepository(ABC):
    """
    Interfaz para el repositorio de Estimations.

    Define las operaciones de persistencia para la entidad Estimation.
    """

    @abstractmethod
    def save(self, estimation: Estimation) -> None:
        """
        Guarda una estimation.

        Args:
            estimation: Estimation a guardar
        """
        pass

    @abstractmethod
    def save_batch(self, estimations: list[Estimation]) -> None:
        """
        Guarda múltiples estimations.

        Args:
            estimations: Lista de estimations a guardar
        """
        pass

    @abstractmethod
    def find_by_id(self, estimation_id: UUID) -> Optional[Estimation]:
        """
        Busca una estimation por su ID.

        Args:
            estimation_id: Identificador de la estimation

        Returns:
            Estimation encontrada o None
        """
        pass

    @abstractmethod
    def find_by_processing(
        self, processing_id: UUID
    ) -> list[Estimation]:
        """
        Busca todas las estimations de un processing.

        Args:
            processing_id: Identificador del processing

        Returns:
            Lista de estimations encontradas
        """
        pass

    @abstractmethod
    def find_by_case(self, case_id: UUID) -> Optional[Estimation]:
        """
        Busca la estimation de un case.

        Args:
            case_id: Identificador del case

        Returns:
            Estimation encontrada o None
        """
        pass
