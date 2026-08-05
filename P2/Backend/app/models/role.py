from dataclasses import dataclass
from enum import StrEnum


class RoleName(StrEnum):
    """Roles permitidos por la aplicación."""

    ADMIN = "ADMIN"
    CLIENTE = "CLIENTE"


@dataclass(frozen=True, slots=True)
class Role:
    """Representa un rol del sistema."""

    id: int
    name: RoleName
    description: str | None