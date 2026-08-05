from abc import ABC, abstractmethod
from uuid import UUID

from app.models.user import User


class UserRepositoryInterface(ABC):
    """Define las operaciones necesarias para administrar usuarios."""

    @abstractmethod
    def find_by_email(self, email: str) -> User | None:
        """Busca un usuario por su correo."""

        raise NotImplementedError

    @abstractmethod
    def find_by_id(self, user_id: UUID) -> User | None:
        """Busca un usuario por su identificador."""

        raise NotImplementedError

    @abstractmethod
    def create(
        self,
        first_name: str,
        last_name: str,
        email: str,
        password_hash: str,
        role_id: int,
    ) -> User:
        """Crea un nuevo usuario."""

        raise NotImplementedError

    @abstractmethod
    def update_last_login(self, user_id: UUID) -> None:
        """Actualiza la fecha del último inicio de sesión."""

        raise NotImplementedError