from typing import Any

from fastapi import APIRouter, HTTPException

from app.factories.registry import IntegrationRegistry
from app.services.normalization_service import NormalizationService

router = APIRouter(prefix="/api/v1/viagens", tags=["Viagens"])

_registry = IntegrationRegistry.default()
_service = NormalizationService(_registry)


@router.post("/normalizar")
def normalizar(payload: list[dict[str, Any]]):
    try:
        return _service.normalize(payload)
    except Exception as exc:
        if hasattr(exc, "to_detail"):
            raise HTTPException(status_code=422, detail=exc.to_detail())
        raise
