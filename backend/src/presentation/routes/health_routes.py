from fastapi import APIRouter

from constants.http import HTTP_STATUS_OK

router = APIRouter()


@router.get("/health", status_code=HTTP_STATUS_OK)
async def health_check() -> dict[str, object]:
    return {
        "is_success": True,
        "data": {"status": "healthy"},
    }
