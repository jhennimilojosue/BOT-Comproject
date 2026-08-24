from uuid import uuid4

import pytest

from app.application.dto.process_cases_dto import ProcessCasesRequest
from app.application.use_cases.process_cases import (
    CatalogServiceProtocol,
    ProcessCasesUseCase,
)


class FakeCaseRepository:
    def __init__(self, cases):
        self.cases = cases
        self.saved = []

    def find_by_upload(self, upload_id):
        return self.cases

    def save_batch(self, cases):
        self.saved.extend(cases)
        return cases


class FakeProcessingRepository:
    def __init__(self):
        self.items = {}

    def save(self, processing):
        processing.setdefault("created_at", "2026-08-23T00:00:00")
        self.items[processing["id"]] = dict(processing)
        return processing

    def update(self, processing):
        self.items[processing["id"]] = dict(processing)
        return processing


class FakeRejectionRepository:
    def __init__(self):
        self.saved = []

    def save_batch(self, rejections):
        self.saved.extend(rejections)
        return rejections


class FakeCatalogService:
    def __init__(self, valid_responsible=True, processable_status=True, category_configured=True):
        self.valid_responsible = valid_responsible
        self.processable_status = processable_status
        self.category_configured = category_configured

    def is_valid_responsible(self, responsible_id) -> bool:
        return self.valid_responsible

    def is_processable_status(self, status: str) -> bool:
        return self.processable_status

    def is_category_configured(self, category: str) -> bool:
        return self.category_configured


class FakeEstimationEngine:
    def __init__(self, result=None):
        self.result = result
        self.calls = []

    async def estimate(self, case_context, config):
        from app.domain.estimation.value_objects.estimation_result import EstimationResult

        if self.result is None:
            return EstimationResult(estimated_minutes=45, description="Trabajo realizado.", status="VALID")
        return self.result


def make_case(**overrides):
    case = {
        "id": str(uuid4()),
        "case_code": "INC001245",
        "responsible_name": "Carlos Rodríguez",
        "project": "Hospital Militar",
        "status": "Solucionado",
        "final_category": "Ingreso de Huella",
        "description": "Problema con dispositivo.",
        "solution": "Se configuró.",
    }
    case.update(overrides)
    return case


def make_use_case(cases, catalog=None, estimation=None):
    case_repo = FakeCaseRepository(cases)
    processing_repo = FakeProcessingRepository()
    rejection_repo = FakeRejectionRepository()
    catalog = catalog or FakeCatalogService()
    estimation = estimation or FakeEstimationEngine()

    use_case = ProcessCasesUseCase(
        case_repository=case_repo,
        processing_repository=processing_repo,
        rejection_repository=rejection_repo,
        catalog_service=catalog,
        estimation_engine=estimation,
    )
    return use_case, rejection_repo


def make_request():
    return ProcessCasesRequest(upload_id=uuid4(), processing_id=uuid4(), responsible_id=uuid4())


class TestProcessCasesHappyPath:
    async def test_should_complete_with_valid_cases(self):
        use_case, rejections = make_use_case([make_case(), make_case(case_code="INC001246")])

        response = await use_case.execute(make_request(), None)

        assert response.status == "COMPLETED"
        assert response.total_cases == 2
        assert response.processed_cases == 2
        assert response.rejected_cases == 0
        assert len(rejections.saved) == 0

    async def test_should_allow_partial_processing(self):
        use_case, _ = make_use_case(
            [make_case()],
            estimation=FakeEstimationEngine(
                result=__import__(
                    "app.domain.estimation.value_objects.estimation_result", fromlist=["EstimationResult"]
                ).EstimationResult(
                    estimated_minutes=10,
                    description="Fuera de rango.",
                    status="REJECTED",
                    rejection_reason="ESTIMATION_OUT_OF_RANGE",
                )
            ),
            catalog=FakeCatalogService(),
        )

        response = await use_case.execute(make_request(), None)

        assert response.status == "COMPLETED"
        assert response.processed_cases == 0
        assert response.rejected_cases == 1


class TestProcessCasesValidation:
    async def test_should_raise_when_responsible_is_invalid(self):
        use_case, _ = make_use_case([], catalog=FakeCatalogService(valid_responsible=False))

        with pytest.raises(ValueError):
            await use_case.execute(make_request(), None)

    async def test_should_reject_case_without_case_code(self):
        use_case, rejections = make_use_case([make_case(case_code="")])

        response = await use_case.execute(make_request(), None)

        assert response.rejected_cases == 1
        assert rejections.saved[0]["reason_code"] == "INCOMPLETE_DATA"

    async def test_should_reject_case_without_final_category(self):
        use_case, rejections = make_use_case([make_case(final_category="")])

        response = await use_case.execute(make_request(), None)

        assert response.rejected_cases == 1
        assert rejections.saved[0]["reason_code"] == "INCOMPLETE_DATA"

    async def test_should_reject_case_with_non_processable_status(self):
        use_case, rejections = make_use_case(
            [make_case()], catalog=FakeCatalogService(processable_status=False)
        )

        response = await use_case.execute(make_request(), None)

        assert response.rejected_cases == 1
        assert rejections.saved[0]["reason_code"] == "STATUS_NOT_PROCESSABLE"

    async def test_should_reject_case_with_unconfigured_category(self):
        use_case, rejections = make_use_case(
            [make_case()], catalog=FakeCatalogService(category_configured=False)
        )

        response = await use_case.execute(make_request(), None)

        assert response.rejected_cases == 1
        assert rejections.saved[0]["reason_code"] == "CATEGORY_NOT_CONFIGURED"


class TestProcessCasesCounters:
    async def test_counters_must_sum_total_when_completed(self):
        cases = [
            make_case(case_code="INC001"),
            make_case(case_code="INC002", status="Cancelado"),
        ]
        use_case, _ = make_use_case(cases, catalog=FakeCatalogService())

        response = await use_case.execute(make_request(), None)

        assert response.total_cases == 2
        assert response.total_cases == response.processed_cases + response.rejected_cases
