from fastapi import Request
from fastapi import Response

from app.config.settings import Settings
from app.exceptions.auth_exception import (
    MissingTokenException,
)


class CookieService:
    """Administra la cookie utilizada para la autenticación."""

    def set_auth_cookie(
        self,
        response: Response,
        token: str,
    ) -> None:
        cookie_lifetime = (
            Settings.JWT_EXPIRATION_MINUTES
            + Settings.JWT_RENEWAL_WINDOW_MINUTES
        ) * 60

        response.set_cookie(
            key=Settings.COOKIE_NAME,
            value=token,
            max_age=cookie_lifetime,
            httponly=True,
            secure=Settings.COOKIE_SECURE,
            samesite=Settings.COOKIE_SAMESITE,
            path=Settings.COOKIE_PATH,
        )

    def get_auth_token(self, request: Request) -> str:
        token = request.cookies.get(Settings.COOKIE_NAME)

        if not token:
            raise MissingTokenException()

        return token

    def delete_auth_cookie(self, response: Response) -> None:
        response.delete_cookie(
            key=Settings.COOKIE_NAME,
            path=Settings.COOKIE_PATH,
        )