from fastapi import APIRouter, Depends, HTTPException

from app.api.schemas.api_schemas import ResponsiblesResponse

router = APIRouter(prefix="/api/v1", tags=["responsibles"])


def get_catalog_service():
    raise NotImplementedError("Dependency injection pending Dev 1 interfaces")


@router.get("/responsibles", response_model=ResponsiblesResponse)
async def get_responsibles(catalog_service=Depends(get_catalog_service)):
    try:
        responsibles = catalog_service.get_active_responsibles()
    except Exception:
        raise HTTPException(
            status_code=503,
            detail={"error": {"code": "CATALOG_SERVICE_ERROR", "message": "Catalog Service unavailable"}},
        )

    items = [{"id": r.id, "name": r.name} for r in responsibles]
    return ResponsiblesResponse(items=items, total=len(items))
