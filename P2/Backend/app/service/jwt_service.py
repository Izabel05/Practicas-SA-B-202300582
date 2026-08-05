from datetime import datetime
from datetime import timedelta
from datetime import timezone
from uuid import UUID

import jwt
from jwt import ExpiredSignatureError
from jwt import InvalidTokenError

from app.config.settings import Settings
from app.exceptions.auth_exception import ExpiredTokenException
from app.exceptions.auth_exception import InvalidTokenException
from app.exceptions.auth_exception import (
    TokenRenewalExpiredException,
)
from app.models.role import RoleName
from app.service.interfaces.token_service_interface import (
    TokenServiceInterface,
)


class JWTService(TokenServiceInterface):
    """Genera, valida y renueva tokens JWT."""

    def create_token(
        self,
        user_id: UUID,
        role: RoleName,
    ) -> str:
        now = datetime.now(timezone.utc)
        expiration = now + timedelta(
            minutes=Settings.JWT_EXPIRATION_MINUTES,
        )

        payload = {
            "sub": str(user_id),
            "role": role.value,
            "iat": now,
            "exp": expiration,
            "iss": Settings.JWT_ISSUER,
            "aud": Settings.JWT_AUDIENCE,
        }

        return jwt.encode(
            payload=payload,
            key=Settings.JWT_SECRET_KEY,
            algorithm=Settings.JWT_ALGORITHM,
        )

    def validate_token(self, token: str) -> dict:
        try:
            return jwt.decode(
                jwt=token,
                key=Settings.JWT_SECRET_KEY,
                algorithms=[Settings.JWT_ALGORITHM],
                issuer=Settings.JWT_ISSUER,
                audience=Settings.JWT_AUDIENCE,
            )

        except ExpiredSignatureError as error:
            raise ExpiredTokenException() from error

        except InvalidTokenError as error:
            raise InvalidTokenException() from error

    def renew_token(self, expired_token: str) -> str:
        payload = self._decode_for_renewal(expired_token)

        expiration = datetime.fromtimestamp(
            payload["exp"],
            tz=timezone.utc,
        )

        now = datetime.now(timezone.utc)

        elapsed_time = now - expiration
        renewal_window = timedelta(
            minutes=Settings.JWT_RENEWAL_WINDOW_MINUTES,
        )

        if elapsed_time < timedelta(0):
            raise InvalidTokenException()

        if elapsed_time > renewal_window:
            raise TokenRenewalExpiredException()

        try:
            user_id = UUID(payload["sub"])
            role = RoleName(payload["role"])

        except (ValueError, KeyError) as error:
            raise InvalidTokenException() from error

        return self.create_token(
            user_id=user_id,
            role=role,
        )

    @staticmethod
    def _decode_for_renewal(token: str) -> dict:
        """Lee un token expirado conservando la validación de firma."""

        try:
            return jwt.decode(
                jwt=token,
                key=Settings.JWT_SECRET_KEY,
                algorithms=[Settings.JWT_ALGORITHM],
                issuer=Settings.JWT_ISSUER,
                audience=Settings.JWT_AUDIENCE,
                options={
                    "verify_exp": False,
                    "require": [
                        "sub",
                        "role",
                        "iat",
                        "exp",
                        "iss",
                        "aud",
                    ],
                },
            )

        except InvalidTokenError as error:
            raise InvalidTokenException() from error