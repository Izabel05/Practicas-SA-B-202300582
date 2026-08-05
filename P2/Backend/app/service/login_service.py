from dataclasses import dataclass

from app.exceptions.auth_exception import (
    InactiveUserException,
)
from app.exceptions.auth_exception import (
    InvalidCredentialsException,
)
from app.repository.interface.user_repository_interface import (
    UserRepositoryInterface,
)
from app.schemas.auth_schema import AuthSchema
from app.schemas.auth_schema import AuthenticatedUserResponse
from app.schemas.login_schema import LoginSchema
from app.service.interfaces.password_service_interface import (
    PasswordServiceInterface,
)
from app.service.interfaces.token_service_interface import (
    TokenServiceInterface,
)


@dataclass(frozen=True, slots=True)
class LoginResult:
    """Resultado interno del inicio de sesión."""

    response: AuthSchema
    token: str


class LoginService:
    """Valida las credenciales e inicia una sesión."""

    def __init__(
        self,
        user_repository: UserRepositoryInterface,
        password_service: PasswordServiceInterface,
        token_service: TokenServiceInterface,
    ) -> None:
        self._user_repository = user_repository
        self._password_service = password_service
        self._token_service = token_service

    def execute(self, schema: LoginSchema) -> LoginResult:
        user = self._user_repository.find_by_email(schema.email)

        if user is None:
            raise InvalidCredentialsException()

        if not user.is_active:
            raise InactiveUserException()

        password_is_valid = self._password_service.verify_password(
            password=schema.password,
            password_hash=user.password_hash,
        )

        if not password_is_valid:
            raise InvalidCredentialsException()

        token = self._token_service.create_token(
            user_id=user.id,
            role=user.role_name,
        )

        self._user_repository.update_last_login(user.id)

        auth_response = AuthSchema(
            message="Inicio de sesión exitoso.",
            user=AuthenticatedUserResponse(
                id=user.id,
                first_name=user.first_name,
                last_name=user.last_name,
                email=user.email,
                role=user.role_name,
            ),
        )

        return LoginResult(
            response=auth_response,
            token=token,
        )