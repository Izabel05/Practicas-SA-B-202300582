from functools import lru_cache

from app.config.database import Database
from app.controller.login_controller import LoginController
from app.controller.registro_controller import RegistroController
from app.controller.token_controller import TokenController
from app.repository.role_repository import RoleRepository
from app.repository.user_repository import UserRepository
from app.service.cookie_service import CookieService
from app.service.data_encryption_service import DataEncryptionService
from app.service.jwt_service import JWTService
from app.service.login_service import LoginService
from app.service.password_service import PasswordService
from app.service.refresh_token_service import RefreshTokenService
from app.service.resgitro_service import RegistroService
from typing import Annotated, Callable

from fastapi import Depends, Request

from app.exceptions.auth_exception import UnauthorizedRoleException
from app.models.role import RoleName
from app.service.cookie_service import CookieService
from app.service.interfaces.token_service_interface import (
    TokenServiceInterface,
)

@lru_cache
def get_database() -> Database:
    """Devuelve la instancia compartida de la base de datos."""

    return Database()


@lru_cache
def get_password_service() -> PasswordService:
    """Devuelve el servicio de contraseñas."""

    return PasswordService()


@lru_cache
def get_token_service() -> JWTService:
    """Devuelve el servicio JWT."""

    return JWTService()


@lru_cache
def get_cookie_service() -> CookieService:
    """Devuelve el servicio de cookies."""

    return CookieService()


@lru_cache
def get_data_encryption_service() -> DataEncryptionService:
    """Devuelve el servicio compartido de cifrado de datos."""

    return DataEncryptionService()


def get_user_repository() -> UserRepository:
    """Construye el repositorio de usuarios."""

    return UserRepository(
        database=get_database(),
        encryption_service=get_data_encryption_service(),
    )


def get_role_repository() -> RoleRepository:
    """Construye el repositorio de roles."""

    return RoleRepository(
        database=get_database(),
    )


def get_registro_service() -> RegistroService:
    """Construye el servicio de registro."""

    return RegistroService(
        user_repository=get_user_repository(),
        role_repository=get_role_repository(),
        password_service=get_password_service(),
    )


def get_login_service() -> LoginService:
    """Construye el servicio de inicio de sesión."""

    return LoginService(
        user_repository=get_user_repository(),
        password_service=get_password_service(),
        token_service=get_token_service(),
    )


def get_refresh_token_service() -> RefreshTokenService:
    """Construye el servicio de renovación."""

    return RefreshTokenService(
        token_service=get_token_service(),
    )


def get_registro_controller() -> RegistroController:
    """Construye el controlador de registro."""

    return RegistroController(
        registro_service=get_registro_service(),
    )


def get_login_controller() -> LoginController:
    """Construye el controlador de login."""

    return LoginController(
        login_service=get_login_service(),
        cookie_service=get_cookie_service(),
    )


def get_token_controller() -> TokenController:
    """Construye el controlador de renovación."""

    return TokenController(
        refresh_token_service=get_refresh_token_service(),
        cookie_service=get_cookie_service(),
    )
def get_current_user(
    request: Request,
    cookie_service: Annotated[
        CookieService,
        Depends(get_cookie_service),
    ],
    token_service: Annotated[
        TokenServiceInterface,
        Depends(get_token_service),
    ],
) -> dict:
    """Obtiene y valida el usuario autenticado desde la cookie."""

    token = cookie_service.get_auth_token(request)

    return token_service.validate_token(token)
def require_roles(
    allowed_roles: set[RoleName],
) -> Callable:
    """Crea una dependencia que valida los roles permitidos."""

    def validate_role(
        current_user: Annotated[
            dict,
            Depends(get_current_user),
        ],
    ) -> dict:
        role_value = current_user.get("role")

        try:
            user_role = RoleName(role_value)
        except (ValueError, TypeError):
            raise UnauthorizedRoleException()

        if user_role not in allowed_roles:
            raise UnauthorizedRoleException()

        return current_user

    return validate_role
