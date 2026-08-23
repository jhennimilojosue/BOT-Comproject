from typing import Protocol
from uuid import UUID

from app.application.dto.process_cases_dto import (
    ExcelCaseDTO,
    ProcessableCaseDTO,
    ProcessCasesRequest,
    ProcessCasesResponse,
)
from app.domain.estimation.services.estimation_engine import EstimationEngine
from app.infrastructure.ai.models import AIConfig


class CaseRepositoryProtocol(Protocol):
    def find_by_upload(self, upload_id: UUID) -> list[dict]:
        pass

    def save_batch(self, cases: list[dict]) -> list[dict]:
        pass


class ProcessingRepositoryProtocol(Protocol):
    def save(self, processing: dict) -> dict:
        pass

    def update(self, processing: dict) -> dict:
        pass


class ProcessingRejectionRepositoryProtocol(Protocol):
    def save_batch(self, rejections: list[dict]) -> list[dict]:
        pass


class CatalogServiceProtocol(Protocol):
    def is_valid_responsible(self, responsible_id: UUID) -> bool:
        pass

    def is_processable_status(self, status: str) -> bool:
        pass

    def is_category_configured(self, category: str) -> bool:
        pass


class ProcessCasesUseCase:
    def __init__(
        self,
        case_repository: CaseRepositoryProtocol,
        processing_repository: ProcessingRepositoryProtocol,
        rejection_repository: ProcessingRejectionRepositoryProtocol,
        catalog_service: CatalogServiceProtocol,
        estimation_engine: EstimationEngine,
    ):
        self.case_repository = case_repository
        self.processing_repository = processing_repository
        self.rejection_repository = rejection_repository
        self.catalog_service = catalog_service
        self.estimation_engine = estimation_engine

    async def execute(
        self, request: ProcessCasesRequest, config: AIConfig
    ) -> ProcessCasesResponse:
        processing = {
            "id": request.processing_id,
            "upload_id": request.upload_id,
            "responsible_id": request.responsible_id,
            "status": "PROCESSING",
            "total_cases": 0,
            "processed_cases": 0,
            "rejected_cases": 0,
        }
        processing = self.processing_repository.save(processing)

        if not self.catalog_service.is_valid_responsible(request.responsible_id):
            processing["status"] = "FAILED"
            self.processing_repository.update(processing)
            raise ValueError("Invalid responsible")

        cases = self.case_repository.find_by_upload(request.upload_id)
        processing["total_cases"] = len(cases)

        processable_cases = []
        rejections = []

        for case in cases:
            result = self._validate_case(case, request.responsible_id)
            if result is None:
                processable_cases.append(case)
            else:
                result["processing_id"] = request.processing_id
                rejections.append(result)

        processing["rejected_cases"] += len(rejections)

        estimations = []
        for case in processable_cases:
            try:
                case_context = self._build_case_context(case)
                estimation_result = await self.estimation_engine.estimate(
                    case_context, config
                )
                if estimation_result.status == "VALID":
                    processing["processed_cases"] += 1
                    estimations.append(
                        {
                            "case_id": case["id"],
                            "estimated_minutes": estimation_result.estimated_minutes,
                            "description": estimation_result.description,
                            "status": "VALID",
                        }
                    )
                else:
                    processing["rejected_cases"] += 1
                    rejections.append(
                        {
                            "processing_id": request.processing_id,
                            "case_id": case["id"],
                            "reason_code": "ESTIMATION_OUT_OF_RANGE",
                            "message": f"Estimation {estimation_result.estimated_minutes} out of range",
                        }
                    )
            except Exception as e:
                processing["rejected_cases"] += 1
                rejections.append(
                    {
                        "processing_id": request.processing_id,
                        "case_id": case["id"],
                        "reason_code": "AI_SERVICE_ERROR",
                        "message": str(e),
                    }
                )

        if rejections:
            self.rejection_repository.save_batch(rejections)

        processing["status"] = "COMPLETED"
        self.processing_repository.update(processing)

        return ProcessCasesResponse(
            processing_id=processing["id"],
            total_cases=processing["total_cases"],
            processed_cases=processing["processed_cases"],
            rejected_cases=processing["rejected_cases"],
            status=processing["status"],
            created_at=processing["created_at"],
        )

    def _validate_case(self, case: dict, responsible_id: UUID) -> dict | None:
        if not case.get("case_code"):
            return {
                "processing_id": None,
                "case_id": case["id"],
                "reason_code": "INCOMPLETE_DATA",
                "message": "Missing case code",
            }

        if not case.get("final_category"):
            return {
                "processing_id": None,
                "case_id": case["id"],
                "reason_code": "INCOMPLETE_DATA",
                "message": "Missing final category",
            }

        if not self.catalog_service.is_processable_status(case.get("status", "")):
            return {
                "processing_id": None,
                "case_id": case["id"],
                "reason_code": "STATUS_NOT_PROCESSABLE",
                "message": f"Status not processable: {case.get('status')}",
            }

        if not self.catalog_service.is_category_configured(
            case.get("final_category", "")
        ):
            return {
                "processing_id": None,
                "case_id": case["id"],
                "reason_code": "CATEGORY_NOT_CONFIGURED",
                "message": f"Category not configured: {case.get('final_category')}",
            }

        return None

    def _build_case_context(self, case: dict) -> dict:
        return {
            "codigo": case.get("case_code"),
            "responsable": case.get("responsible_name"),
            "proyecto": case.get("project"),
            "categoria_final": case.get("final_category"),
            "descripcion": case.get("description"),
            "solucion": case.get("solution"),
            "estado": case.get("status"),
        }
