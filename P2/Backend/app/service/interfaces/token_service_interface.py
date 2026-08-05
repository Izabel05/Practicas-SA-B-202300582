from abc import ABC
from abc import abstractmethod
from uuid import UUID

from app.models.role import RoleName


class TokenServiceInterface(ABC):
    """Define las operaciones relacionadas con tokens."""

    @abstractmethod
    def create_token(
        self,
        user_id: UUID,
        role: RoleName,
    ) -> str:
        """Genera un token de acceso."""

        raise NotImplementedError

    @abstractmethod
    def validate_token(self, token: str) -> dict:
        """Valida un token que todavía no ha expirado."""

        raise NotImplementedError

    @abstractmethod
    def renew_token(self, expired_token: str) -> str:
        """Renueva un token dentro del periodo permitido."""

        raise NotImplementedError