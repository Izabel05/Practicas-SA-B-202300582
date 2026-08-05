from fastapi import Response

from app.schemas.auth_schema import AuthSchema
from app.schemas.login_schema import LoginSchema
from app.service.cookie_service import CookieService
from app.service.login_service import LoginService


class LoginController:
    """Coordina la operación HTTP de inicio de sesión."""

    def __init__(
        self,
        login_service: LoginService,
        cookie_service: CookieService,
    ) -> None:
        self._login_service = login_service
        self._cookie_service = cookie_service

    def login(
        self,
        schema: LoginSchema,
        response: Response,
    ) -> AuthSchema:
        result = self._login_service.execute(schema)

        self._cookie_service.set_auth_cookie(
            response=response,
            token=result.token,
        )

        return result.response