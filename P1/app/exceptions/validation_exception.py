from app.exceptions.aplication_exception import (
    ApplicationException,
)


class ValidationException(ApplicationException):
    """
    Indica que los datos recibidos no cumplen con las reglas
    de validación de la aplicación.
    """

    ERROR_CODE = "VALIDATION_ERROR"

    def __init__(
        self,
        errors: dict[str, str],
    ) -> None:
        super().__init__(
            message="Los datos proporcionados no son válidos.",
            error_code=self.ERROR_CODE,
            details={
                "fields": errors,
            },
        )