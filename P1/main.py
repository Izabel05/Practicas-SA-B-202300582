from app.config.database import (
    get_connection,
    verify_database_connection,
)
from app.config.settings import Settings
from app.controllers import SolicitudController
from app.repositories.solicitud_repository import (
    SolicitudRepository,
)
from app.routes import SolicitudRoutes
from app.server import ApiServer
from app.services.solicitud_service import SolicitudService


HOST = "127.0.0.1"
PORT = 8000


def create_application() -> SolicitudRoutes:
    """
    Construye y conecta las dependencias de la aplicación.
    """
    repository = SolicitudRepository(
        connection_factory=get_connection
    )

    service = SolicitudService(
        repository=repository
    )

    controller = SolicitudController(
        service=service
    )

    return SolicitudRoutes(
        controller=controller
    )


def validate_startup() -> None:
    """
    Valida la configuración y la conexión antes de iniciar
    el servidor HTTP.
    """
    Settings.validate()
    verify_database_connection()


def main() -> None:
    """
    Inicializa y ejecuta la aplicación.
    """
    try:
        validate_startup()

        routes = create_application()

        server = ApiServer(
            host=HOST,
            port=PORT,
            routes=routes,
        )

        server.start()

    except RuntimeError as error:
        print(f"Error al iniciar la aplicación: {error}")


if __name__ == "__main__":
    main()