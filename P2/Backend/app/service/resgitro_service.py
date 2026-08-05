from app.exceptions.user_exceptions import (
    UserAlreadyExistsException,
    UserCreationException,
)
from app.models.role import RoleName
from app.repository.interface.role_repository_interface import (
    RoleRepositoryInterface,
)
from app.repository.interface.user_repository_interface import (
    UserRepositoryInterface,
)
from app.schemas.auth_schema import AuthSchema, AuthenticatedUserResponse
from app.schemas.registro_schema import RegisterSchema
from app.service.interfaces.password_service_interface import (
    PasswordServiceInterface,
)


class RegistroService:
    """Coordina el registro público de clientes."""

    def __init__(
        self,
        user_repository: UserRepositoryInterface,
        role_repository: RoleRepositoryInterface,
        password_service: PasswordServiceInterface,
    ) -> None:
        self._user_repository = user_repository
        self._role_repository = role_repository
        self._password_service = password_service

    def execute(self, schema: RegisterSchema) -> AuthSchema:
        existing_user = self._user_repository.find_by_email(schema.email)

        if existing_user:
            raise UserAlreadyExistsException()

        client_role = self._role_repository.find_by_name(
            RoleName.CLIENTE,
        )

        if client_role is None:
            raise UserCreationException()

        password_hash = self._password_service.hash_password(
            schema.password,
        )

        user = self._user_repository.create(
            first_name=schema.first_name,
            last_name=schema.last_name,
            email=schema.email,
            password_hash=password_hash,
            role_id=client_role.id,
        )

        return AuthSchema(
            message="Usuario registrado correctamente.",
            user=AuthenticatedUserResponse(
                id=user.id,
                first_name=user.first_name,
                last_name=user.last_name,
                email=user.email,
                role=user.role_name,
            ),
        )