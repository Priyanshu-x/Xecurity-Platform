from typing import TypeVar, Generic, Optional, Any, Dict, List
from enum import Enum
from pydantic import BaseModel

T = TypeVar('T')

class ErrorType(str, Enum):
    VALIDATION_ERROR = "VALIDATION_ERROR"
    NOT_FOUND = "NOT_FOUND"
    CONFLICT = "CONFLICT"
    UNAUTHORIZED = "UNAUTHORIZED"
    FORBIDDEN = "FORBIDDEN"
    INTERNAL_ERROR = "INTERNAL_ERROR"

class ErrorDetail(BaseModel):
    message: str
    code: ErrorType
    details: Optional[Dict[str, Any]] = None

class Result(Generic[T]):
    """Base class for service results."""
    def __init__(self, is_success: bool, value: Optional[T] = None, error: Optional[ErrorDetail] = None):
        self.is_success = is_success
        self.value = value
        self.error = error

class Success(Result[T]):
    def __init__(self, value: T):
        super().__init__(is_success=True, value=value)

class Failure(Result[T]):
    def __init__(self, message: str, code: ErrorType, details: Optional[Dict[str, Any]] = None):
        error = ErrorDetail(message=message, code=code, details=details)
        super().__init__(is_success=False, error=error)

class ValidationError(Failure[T]):
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message=message, code=ErrorType.VALIDATION_ERROR, details=details)

class NotFoundError(Failure[T]):
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message=message, code=ErrorType.NOT_FOUND, details=details)

class ConflictError(Failure[T]):
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message=message, code=ErrorType.CONFLICT, details=details)
