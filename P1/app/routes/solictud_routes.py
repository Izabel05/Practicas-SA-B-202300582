#rutas
import re
from http import HTTPStatus
from typing import Any

from app.controllers.solicitud_controller import (
    SolicitudController,
)


Response = tuple[dict[str, Any], int]


class SolicitudRoutes:
    """
    Relaciona las rutas HTTP de solicitudes con los métodos
    correspondientes del controlador.

    Esta clase no contiene reglas de negocio ni acceso directo
    a la base de datos.
    """

    RUTA_COLECCION = "/solicitudes"

    PATRON_SOLICITUD = re.compile(
        r"^/solicitudes/(?P<solicitud_id>\d+)$"
    )

    PATRON_ESTADO = re.compile(
        r"^/solicitudes/(?P<solicitud_id>\d+)/estado$"
    )

    def __init__(
        self,
        controller: SolicitudController,
    ) -> None:
        self._controller = controller

    def procesar(
        self,
        metodo: str,
        ruta: str,
        datos: dict[str, Any] | None = None,
    ) -> Response:
        """
        Busca la ruta solicitada y ejecuta el método correspondiente
        del controlador.
        """
        metodo_normalizado = metodo.upper().strip()
        ruta_normalizada = self._normalizar_ruta(ruta)
        datos_recibidos = datos or {}

        if ruta_normalizada == self.RUTA_COLECCION:
            return self._procesar_ruta_coleccion(
                metodo=metodo_normalizado,
                datos=datos_recibidos,
            )

        coincidencia_estado = self.PATRON_ESTADO.fullmatch(
            ruta_normalizada
        )

        if coincidencia_estado:
            return self._procesar_ruta_estado(
                metodo=metodo_normalizado,
                solicitud_id=self._extraer_id(
                    coincidencia_estado
                ),
                datos=datos_recibidos,
            )

        coincidencia_solicitud = (
            self.PATRON_SOLICITUD.fullmatch(
                ruta_normalizada
            )
        )

        if coincidencia_solicitud:
            return self._procesar_ruta_individual(
                metodo=metodo_normalizado,
                solicitud_id=self._extraer_id(
                    coincidencia_solicitud
                ),
                datos=datos_recibidos,
            )

        return self._respuesta_ruta_no_encontrada()

    def _procesar_ruta_coleccion(
        self,
        metodo: str,
        datos: dict[str, Any],
    ) -> Response:
        """
        Procesa las operaciones sobre la colección completa.

        GET  /solicitudes
        POST /solicitudes
        """
        if metodo == "GET":
            return self._controller.obtener_todas()

        if metodo == "POST":
            return self._controller.crear(datos)

        return self._respuesta_metodo_no_permitido(
            metodos_permitidos={"GET", "POST"}
        )

    def _procesar_ruta_individual(
        self,
        metodo: str,
        solicitud_id: int,
        datos: dict[str, Any],
    ) -> Response:
        """
        Procesa las operaciones sobre una solicitud específica.

        GET    /solicitudes/{id}
        PUT    /solicitudes/{id}
        DELETE /solicitudes/{id}
        """
        if metodo == "GET":
            return self._controller.obtener_por_id(
                solicitud_id
            )

        if metodo == "PUT":
            return self._controller.actualizar(
                solicitud_id=solicitud_id,
                datos=datos,
            )

        if metodo == "DELETE":
            return self._controller.eliminar(
                solicitud_id
            )

        return self._respuesta_metodo_no_permitido(
            metodos_permitidos={
                "GET",
                "PUT",
                "DELETE",
            }
        )

    def _procesar_ruta_estado(
        self,
        metodo: str,
        solicitud_id: int,
        datos: dict[str, Any],
    ) -> Response:
        """
        Procesa la actualización exclusiva del estado.

        PATCH /solicitudes/{id}/estado
        """
        if metodo == "PATCH":
            return self._controller.actualizar_estado(
                solicitud_id=solicitud_id,
                datos=datos,
            )

        return self._respuesta_metodo_no_permitido(
            metodos_permitidos={"PATCH"}
        )

    @staticmethod
    def _extraer_id(
        coincidencia: re.Match[str],
    ) -> int:
        """
        Extrae y convierte el identificador encontrado en la URL.
        """
        return int(
            coincidencia.group("solicitud_id")
        )

    @staticmethod
    def _normalizar_ruta(ruta: str) -> str:
        """
        Elimina espacios y la barra final para evitar rutas
        duplicadas como /solicitudes y /solicitudes/.
        """
        ruta_limpia = ruta.strip()

        if ruta_limpia != "/":
            ruta_limpia = ruta_limpia.rstrip("/")

        return ruta_limpia

    @staticmethod
    def _respuesta_ruta_no_encontrada() -> Response:
        """
        Devuelve una respuesta REST cuando el recurso solicitado
        no corresponde con ninguna ruta registrada.
        """
        return (
            {
                "error": {
                    "code": "ROUTE_NOT_FOUND",
                    "message": (
                        "La ruta solicitada no existe."
                    ),
                }
            },
            HTTPStatus.NOT_FOUND,
        )

    @staticmethod
    def _respuesta_metodo_no_permitido(
        metodos_permitidos: set[str],
    ) -> Response:
        """
        Devuelve una respuesta REST cuando la ruta existe,
        pero el método HTTP no está permitido.
        """
        metodos = ", ".join(
            sorted(metodos_permitidos)
        )

        return (
            {
                "error": {
                    "code": "METHOD_NOT_ALLOWED",
                    "message": (
                        "El método HTTP utilizado no está "
                        "permitido para esta ruta."
                    ),
                    "details": {
                        "allowed_methods": metodos,
                    },
                }
            },
            HTTPStatus.METHOD_NOT_ALLOWED,
        )