from app.exceptions.application_exception import ApplicationException


class UserAlreadyExistsException(ApplicationException):
    """Indica que el correo ya se encuentra registrado."""

    def __init__(self) -> None:
        super().__init__(
            message="El correo ya se encuentra registrado.",
            status_code=409,
            error_code="USER_ALREADY_EXISTS",
        )


class UserNotFoundException(ApplicationException):
    """Indica que no se encontró el usuario solicitado."""

    def __init__(self) -> None:
        super().__init__(
            message="Usuario no encontrado.",
            status_code=404,
            error_code="USER_NOT_FOUND",
        )

class UserCreationException(ApplicationException):
    """Indica que no fue posible crear al usuario."""

    def __init__(self) -> None:
        super().__init__(
            message="No fue posible registrar al usuario.",
            status_code=500,
            error_code="USER_CREATION_ERROR",
        )