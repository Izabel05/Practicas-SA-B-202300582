from fastapi import Request
from fastapi import Response

from app.service.cookie_service import CookieService
from app.service.refresh_token_service import (
    RefreshTokenService,
)


class TokenController:
    """Coordina la renovación del token."""

    def __init__(
        self,
        refresh_token_service: RefreshTokenService,
        cookie_service: CookieService,
    ) -> None:
        self._refresh_token_service = refresh_token_service
        self._cookie_service = cookie_service

    def refresh(
        self,
        request: Request,
        response: Response,
    ) -> dict[str, str]:
        expired_token = self._cookie_service.get_auth_token(
            request,
        )

        new_token = self._refresh_token_service.execute(
            expired_token,
        )

        self._cookie_service.set_auth_cookie(
            response=response,
            token=new_token,
        )

        return {
            "message": "Sesión renovada correctamente.",
        }