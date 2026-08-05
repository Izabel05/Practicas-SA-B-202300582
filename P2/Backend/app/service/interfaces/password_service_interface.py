from abc import ABC
from abc import abstractmethod


class PasswordServiceInterface(ABC):
    """Define las operaciones para proteger contraseñas."""

    @abstractmethod
    def hash_password(self, password: str) -> str:
        """Genera un hash irreversible."""

        raise NotImplementedError

    @abstractmethod
    def verify_password(
        self,
        password: str,
        password_hash: str,
    ) -> bool:
        """Comprueba una contraseña contra su hash."""

        raise NotImplementedError