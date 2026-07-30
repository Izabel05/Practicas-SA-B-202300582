from typing import Any


class ApplicationException(Exception):
    """
    Excepción base para los errores controlados de la aplicación.

    No genera respuestas HTTP. Únicamente proporciona información
    estructurada para que la capa Controller pueda interpretarla.
    """

    def __init__(
        self,
        message: str,
        error_code: str,
        details: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(message)

        self.message = message
        self.error_code = error_code
        self.details = details or {}

    def to_dict(self) -> dict[str, Any]:
        """
        Convierte la excepción en una estructura de datos.

        El Controller podrá utilizar esta información para construir
        una respuesta JSON siguiendo las convenciones REST.
        """
        error = {
            "code": self.error_code,
            "message": self.message,
        }

        if self.details:
            error["details"] = self.details

        return error