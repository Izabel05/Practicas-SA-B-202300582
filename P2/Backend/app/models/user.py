from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from app.models.role import RoleName


@dataclass(slots=True)
class User:
    """Representa un usuario dentro del dominio."""

    id: UUID
    first_name: str
    last_name: str
    email: str
    password_hash: str
    role_id: int
    role_name: RoleName
    is_active: bool
    email_verified: bool
    last_login: datetime | None
    created_at: datetime
    updated_at: datetime