from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.exceptions.application_exception import ApplicationException


def register_exception_handlers(app: FastAPI) -> None:
    """Registra el manejo global de errores controlados."""

    @app.exception_handler(ApplicationException)
    async def handle_application_exception(
        request: Request,
        exception: ApplicationException,
    ) -> JSONResponse:
        return JSONResponse(
            status_code=exception.status_code,
            content={
                "error": {
                    "code": exception.error_code,
                    "message": exception.message,
                }
            },
        )