from app.exceptions.aplication_exception import (
    ApplicationException,
)


class SolicitudNotFoundException(ApplicationException):
    """
    Indica que no se encontró una solicitud con el identificador
    proporcionado.
    """

    ERROR_CODE = "SOLICITUD_NOT_FOUND"

    def __init__(self, solicitud_id: int) -> None:
        message = (
            f"No existe una solicitud con el id {solicitud_id}."
        )

        details = {
            "solicitud_id": solicitud_id,
        }

        super().__init__(
            message=message,
            error_code=self.ERROR_CODE,
            details=details,
        )