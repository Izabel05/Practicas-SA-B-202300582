from uuid import UUID

from pydantic import BaseModel
from pydantic import ConfigDict
from pydantic import EmailStr

from app.models.role import RoleName


class AuthenticatedUserResponse(BaseModel):
    """Información pública del usuario autenticado."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    first_name: str
    last_name: str
    email: EmailStr
    role: RoleName


class AuthSchema(BaseModel):
    """Respuesta del registro o inicio de sesión."""

    message: str
    user: AuthenticatedUserResponse