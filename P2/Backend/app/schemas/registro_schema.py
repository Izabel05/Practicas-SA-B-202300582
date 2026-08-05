from pydantic import BaseModel
from pydantic import EmailStr
from pydantic import Field
from pydantic import field_validator
from pydantic import model_validator


class RegisterSchema(BaseModel):
    """Datos recibidos para registrar un cliente."""

    first_name: str = Field(
        min_length=2,
        max_length=100,
        examples=["Jeremy"],
    )

    last_name: str = Field(
        min_length=2,
        max_length=100,
        examples=["Orellana"],
    )

    email: EmailStr = Field(
        examples=["jeremy@example.com"],
    )

    password: str = Field(
        min_length=8,
        max_length=128,
    )

    password_confirmation: str = Field(
        min_length=8,
        max_length=128,
    )

    @field_validator("first_name", "last_name")
    @classmethod
    def normalize_names(cls, value: str) -> str:
        normalized_value = " ".join(value.strip().split())

        if not normalized_value:
            raise ValueError("El campo no puede estar vacío.")

        return normalized_value

    @field_validator("email")
    @classmethod
    def normalize_email(cls, value: EmailStr) -> str:
        return str(value).strip().lower()

    @model_validator(mode="after")
    def validate_password_confirmation(self) -> "RegisterSchema":
        if self.password != self.password_confirmation:
            raise ValueError("Las contraseñas no coinciden.")

        return self