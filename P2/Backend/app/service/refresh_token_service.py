from app.service.interfaces.token_service_interface import (
    TokenServiceInterface,
)


class RefreshTokenService:
    """Coordina la renovación de una sesión expirada."""

    def __init__(
        self,
        token_service: TokenServiceInterface,
    ) -> None:
        self._token_service = token_service

    def execute(self, expired_token: str) -> str:
        return self._token_service.renew_token(expired_token)