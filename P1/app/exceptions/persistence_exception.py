from app.exceptions.aplication_exception import ApplicationException


class PersistenceException(ApplicationException):
    """
    Indica que ocurrió un error durante una operación de
    persistencia.

    No expone información sensible de PostgreSQL, NeonDB,
    consultas SQL ni credenciales.
    """

    ERROR_CODE = "PERSISTENCE_ERROR"

    def __init__(
        self,
        operation: str,
    ) -> None:
        super().__init__(
            message=(
                "No fue posible completar la operación solicitada."
            ),
            error_code=self.ERROR_CODE,
            details={
                "operation": operation,
            },
        )