from fastapi import HTTPException, status
from app.common.result import Result, ErrorType, ErrorDetail

def handle_result(result: Result):
    """
    Translates a Result object into a successful return value or raises the appropriate HTTPException.
    """
    if result.is_success:
        return result.value
        
    error: ErrorDetail = result.error
    
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    
    if error.code == ErrorType.NOT_FOUND:
        status_code = status.HTTP_404_NOT_FOUND
    elif error.code == ErrorType.VALIDATION_ERROR:
        status_code = status.HTTP_422_UNPROCESSABLE_ENTITY
    elif error.code == ErrorType.CONFLICT:
        status_code = status.HTTP_409_CONFLICT
    elif error.code == ErrorType.UNAUTHORIZED:
        status_code = status.HTTP_401_UNAUTHORIZED
    elif error.code == ErrorType.FORBIDDEN:
        status_code = status.HTTP_403_FORBIDDEN
        
    raise HTTPException(
        status_code=status_code,
        detail={
            "message": error.message,
            "code": error.code.value,
            "details": error.details
        }
    )
