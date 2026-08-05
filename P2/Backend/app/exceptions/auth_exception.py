from app.exceptions.application_exception import ApplicationException


class InvalidCredentialsException(ApplicationException):
    """Indica que las credenciales son incorrectas."""

    def __init__(self) -> None:
        super().__init__(
            message="Correo o contraseña incorrectos.",
            status_code=401,
            error_code="INVALID_CREDENTIALS",
        )


class InactiveUserException(ApplicationException):
    """Indica que la cuenta está desactivada."""

    def __init__(self) -> None:
        super().__init__(
            message="La cuenta de usuario se encuentra desactivada.",
            status_code=403,
            error_code="INACTIVE_USER",
        )


class InvalidTokenException(ApplicationException):
    """Indica que el token no es válido."""

    def __init__(self) -> None:
        super().__init__(
            message="El token de autenticación no es válido.",
            status_code=401,
            error_code="INVALID_TOKEN",
        )


class TokenRenewalExpiredException(ApplicationException):
    """Indica que terminó la ventana de renovación."""

    def __init__(self) -> None:
        super().__init__(
            message=(
                "La sesión ya no puede renovarse. "
                "Inicia sesión nuevamente."
            ),
            status_code=401,
            error_code="TOKEN_RENEWAL_EXPIRED",
        )

class MissingTokenException(ApplicationException):
    """Indica que la cookie de autenticación no existe."""

    def __init__(self) -> None:
        super().__init__(
            message="No se encontró una sesión activa.",
            status_code=401,
            error_code="MISSING_TOKEN",
        )
class ExpiredTokenException(ApplicationException):
    """Indica que el token ya expiró."""

    def __init__(self) -> None:
        super().__init__(
            message="La sesión ha expirado.",
            status_code=401,
            error_code="EXPIRED_TOKEN",
        )