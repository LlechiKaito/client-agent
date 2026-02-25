from fastapi import Request
from fastapi.responses import JSONResponse

from application.errors.application_error import ApplicationError
from constants.http import HTTP_STATUS_INTERNAL_SERVER_ERROR


async def application_error_handler(_request: Request, exc: ApplicationError) -> JSONResponse:
    return JSONResponse(
        status_code=exc.status,
        content={
            "is_success": False,
            "message": exc.message,
            "code": exc.code,
        },
    )


async def unhandled_error_handler(_request: Request, _exc: Exception) -> JSONResponse:
    return JSONResponse(
        status_code=HTTP_STATUS_INTERNAL_SERVER_ERROR,
        content={
            "is_success": False,
            "message": "Internal server error",
            "code": "INTERNAL_SERVER_ERROR",
        },
    )
