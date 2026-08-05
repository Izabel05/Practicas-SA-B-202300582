from argon2 import PasswordHasher
from argon2.exceptions import InvalidHashError
from argon2.exceptions import VerificationError
from argon2.exceptions import VerifyMismatchError

from app.service.interfaces.password_service_interface import (
    PasswordServiceInterface,
)


class PasswordService(PasswordServiceInterface):
    """Genera y verifica hashes Argon2id."""

    def __init__(self) -> None:
        self._password_hasher = PasswordHasher()

    def hash_password(self, password: str) -> str:
        return self._password_hasher.hash(password)

    def verify_password(
        self,
        password: str,
        password_hash: str,
    ) -> bool:
        try:
            return self._password_hasher.verify(
                password_hash,
                password,
            )

        except (
            VerifyMismatchError,
            VerificationError,
            InvalidHashError,
        ):
            return False