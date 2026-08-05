from app.schemas.auth_schema import AuthSchema
from app.schemas.registro_schema import RegisterSchema
from app.service.resgitro_service import RegistroService


class RegistroController:
    """Coordina la operación HTTP de registro."""

    def __init__(
        self,
        registro_service: RegistroService,
    ) -> None:
        self._registro_service = registro_service

    def register(
        self,
        schema: RegisterSchema,
    ) -> AuthSchema:
        return self._registro_service.execute(schema)