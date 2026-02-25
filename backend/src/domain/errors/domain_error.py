from dataclasses import dataclass


@dataclass(frozen=True)
class ErrorDefinition:
    message: str
    code: str
    status: int


DOMAIN_ERRORS = {
    "NOT_FOUND": ErrorDefinition(
        message="Resource not found",
        code="NOT_FOUND",
        status=404,
    ),
    "VALIDATION_ERROR": ErrorDefinition(
        message="Validation error",
        code="VALIDATION_ERROR",
        status=400,
    ),
    "UNAUTHORIZED": ErrorDefinition(
        message="Unauthorized",
        code="UNAUTHORIZED",
        status=401,
    ),
    "FORBIDDEN": ErrorDefinition(
        message="Forbidden",
        code="FORBIDDEN",
        status=403,
    ),
    "CONFLICT": ErrorDefinition(
        message="Resource conflict",
        code="CONFLICT",
        status=409,
    ),
}
