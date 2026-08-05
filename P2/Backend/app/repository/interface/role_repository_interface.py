from abc import ABC, abstractmethod

from app.models.role import Role, RoleName


class RoleRepositoryInterface(ABC):
    """Define las operaciones necesarias para consultar roles."""

    @abstractmethod
    def find_by_name(self, role_name: RoleName) -> Role | None:
        """Busca un rol por su nombre."""

        raise NotImplementedError