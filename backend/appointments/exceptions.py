from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import exception_handler


class AppError(Exception):
    status_code = status.HTTP_400_BAD_REQUEST
    code = "bad_request"

    def __init__(self, message):
        super().__init__(message)
        self.message = message


class NotFoundError(AppError):
    status_code = status.HTTP_404_NOT_FOUND
    code = "not_found"


class ConflictError(AppError):
    status_code = status.HTTP_409_CONFLICT
    code = "conflict"


def custom_exception_handler(exc, context):
    if isinstance(exc, AppError):
        return Response(
            {"error": {"code": exc.code, "message": exc.message}},
            status=exc.status_code,
        )

    response = exception_handler(exc, context)
    if response is None:
        return None

    if response.status_code == status.HTTP_400_BAD_REQUEST:
        response.data = {
            "error": {
                "code": "validation_error",
                "message": "Request validation failed.",
                "details": response.data,
            }
        }
    else:
        detail = response.data.get("detail", "Request failed.") if isinstance(response.data, dict) else "Request failed."
        response.data = {"error": {"code": "error", "message": str(detail)}}
    return response
