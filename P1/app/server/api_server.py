from functools import partial
from http.server import ThreadingHTTPServer
from typing import TypeAlias

from app.routes import SolicitudRoutes
from app.server.request_handler import ApiRequestHandler


ServerAddress: TypeAlias = tuple[str, int]


class ApiServer:
    """
    Administra el ciclo de vida del servidor HTTP de la API.
    """

    def __init__(
        self,
        host: str,
        port: int,
        routes: SolicitudRoutes,
    ) -> None:
        self._host = host
        self._port = port

        request_handler = partial(
            ApiRequestHandler,
            routes=routes,
        )

        self._server = ThreadingHTTPServer(
            (self._host, self._port),
            request_handler,
        )

    @property
    def address(self) -> ServerAddress:
        """
        Devuelve la dirección real utilizada por el servidor.
        """
        host, port = self._server.server_address

        return str(host), int(port)

    def start(self) -> None:
        """
        Inicia el servidor y lo mantiene escuchando peticiones.
        """
        host, port = self.address

        print(
            f"Servidor iniciado en http://{host}:{port}"
        )
        print("Presiona Ctrl + C para detenerlo.")

        try:
            self._server.serve_forever()
        except KeyboardInterrupt:
            print("\nDeteniendo servidor...")
        finally:
            self.stop()

    def stop(self) -> None:
        """
        Cierra los recursos utilizados por el servidor.
        """
        self._server.server_close()
        print("Servidor detenido correctamente.")