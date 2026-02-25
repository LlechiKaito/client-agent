from constants.http import (
    HTTP_STATUS_BAD_REQUEST,
    HTTP_STATUS_CONFLICT,
    HTTP_STATUS_FORBIDDEN,
    HTTP_STATUS_NOT_FOUND,
    HTTP_STATUS_UNAUTHORIZED,
)


class ApplicationError(Exception):
    def __init__(self, message: str, code: str, status: int) -> None:
        super().__init__(message)
        self.message = message
        self.code = code
        self.status = status


class ValidationError(ApplicationError):
    def __init__(self, message: str, code: str = "VALIDATION_ERROR") -> None:
        super().__init__(message=message, code=code, status=HTTP_STATUS_BAD_REQUEST)


class UnauthorizedError(ApplicationError):
    def __init__(self, message: str, code: str = "UNAUTHORIZED") -> None:
        super().__init__(message=message, code=code, status=HTTP_STATUS_UNAUTHORIZED)


class ForbiddenError(ApplicationError):
    def __init__(self, message: str, code: str = "FORBIDDEN") -> None:
        super().__init__(message=message, code=code, status=HTTP_STATUS_FORBIDDEN)


class NotFoundError(ApplicationError):
    def __init__(self, message: str, code: str = "NOT_FOUND") -> None:
        super().__init__(message=message, code=code, status=HTTP_STATUS_NOT_FOUND)


class ConflictError(ApplicationError):
    def __init__(self, message: str, code: str = "CONFLICT") -> None:
        super().__init__(message=message, code=code, status=HTTP_STATUS_CONFLICT)
