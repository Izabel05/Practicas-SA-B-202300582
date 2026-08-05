from pydantic import BaseModel
from pydantic import EmailStr
from pydantic import Field
from pydantic import field_validator


class LoginSchema(BaseModel):
    """Credenciales recibidas para iniciar sesión."""

    email: EmailStr = Field(
        examples=["user@example.com"],
    )

    password: str = Field(
        min_length=1,
        max_length=128,
    )

    @field_validator("email")
    @classmethod
    def normalize_email(cls, value: EmailStr) -> str:
        return str(value).strip().lower()