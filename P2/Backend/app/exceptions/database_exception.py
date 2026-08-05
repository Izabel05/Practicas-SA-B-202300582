from app.exceptions.application_exception import ApplicationException


class DatabaseConnectionException(ApplicationException):
    """Indica que no fue posible conectarse con la base de datos."""

    def __init__(
        self,
        message: str = "No fue posible conectar con la base de datos.",
    ) -> None:
        super().__init__(
            message=message,
            status_code=503,
            error_code="DATABASE_CONNECTION_ERROR",
        )


class DatabaseOperationException(ApplicationException):
    """Indica que una operación de base de datos falló."""

    def __init__(
        self,
        message: str = "No fue posible completar la operación.",
    ) -> None:
        super().__init__(
            message=message,
            status_code=500,
            error_code="DATABASE_OPERATION_ERROR",
        )