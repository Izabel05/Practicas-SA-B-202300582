from decimal import Decimal
from http import HTTPStatus
from typing import Any

from app.exceptions import (
    ApplicationException,
    PersistenceException,
    SolicitudNotFoundException,
    ValidationException,
)
from app.models.sollicitud_model import Solicitud
from app.schemas.solicitud_schemas import (
    validar_actualizacion_estado,
    validar_solicitud,
)
from app.services.solicitud_service import SolicitudService


Response = tuple[dict[str, Any], int]


class SolicitudController:
    """
    Coordina las operaciones HTTP relacionadas con solicitudes.
    """

    def __init__(self, service: SolicitudService) -> None:
        self._service = service

    def crear(self, datos: dict[str, Any]) -> Response:
        try:
            self._validar_datos_solicitud(datos)

            solicitud = self._crear_modelo(datos)
            solicitud_creada = self._service.crear(solicitud)

            return (
                {
                    "message": "Solicitud creada correctamente.",
                    "data": solicitud_creada.to_dict(),
                },
                HTTPStatus.CREATED,
            )

        except ApplicationException as error:
            return self._crear_respuesta_error(error)

        except Exception:
            return self._crear_error_interno()

    def obtener_todas(self) -> Response:
        try:
            solicitudes = self._service.obtener_todas()

            return (
                {
                    "data": [
                        solicitud.to_dict()
                        for solicitud in solicitudes
                    ],
                    "total": len(solicitudes),
                },
                HTTPStatus.OK,
            )

        except ApplicationException as error:
            return self._crear_respuesta_error(error)

        except Exception:
            return self._crear_error_interno()

    def obtener_por_id(self, solicitud_id: int) -> Response:
        try:
            solicitud = self._service.obtener_por_id(
                solicitud_id
            )

            return (
                {
                    "data": solicitud.to_dict(),
                },
                HTTPStatus.OK,
            )

        except ApplicationException as error:
            return self._crear_respuesta_error(error)

        except Exception:
            return self._crear_error_interno()

    def actualizar(
        self,
        solicitud_id: int,
        datos: dict[str, Any],
    ) -> Response:
        try:
            self._validar_datos_solicitud(datos)

            solicitud = self._crear_modelo(
                datos=datos,
                solicitud_id=solicitud_id,
            )

            solicitud_actualizada = self._service.actualizar(
                solicitud
            )

            return (
                {
                    "message": (
                        "Solicitud actualizada correctamente."
                    ),
                    "data": solicitud_actualizada.to_dict(),
                },
                HTTPStatus.OK,
            )

        except ApplicationException as error:
            return self._crear_respuesta_error(error)

        except Exception:
            return self._crear_error_interno()

    def actualizar_estado(
        self,
        solicitud_id: int,
        datos: dict[str, Any],
    ) -> Response:
        try:
            self._validar_datos_estado(datos)

            solicitud_actualizada = (
                self._service.actualizar_estado(
                    solicitud_id=solicitud_id,
                    estado=datos["estado"],
                )
            )

            return (
                {
                    "message": (
                        "Estado de la solicitud actualizado "
                        "correctamente."
                    ),
                    "data": solicitud_actualizada.to_dict(),
                },
                HTTPStatus.OK,
            )

        except ApplicationException as error:
            return self._crear_respuesta_error(error)

        except Exception:
            return self._crear_error_interno()

    def eliminar(self, solicitud_id: int) -> Response:
        try:
            self._service.eliminar(solicitud_id)

            return {}, HTTPStatus.NO_CONTENT

        except ApplicationException as error:
            return self._crear_respuesta_error(error)

        except Exception:
            return self._crear_error_interno()

    @staticmethod
    def _validar_datos_solicitud(
        datos: dict[str, Any],
    ) -> None:
        errores = validar_solicitud(datos)

        if errores:
            raise ValidationException(errores)

    @staticmethod
    def _validar_datos_estado(
        datos: dict[str, Any],
    ) -> None:
        errores = validar_actualizacion_estado(datos)

        if errores:
            raise ValidationException(errores)

    @staticmethod
    def _crear_modelo(
        datos: dict[str, Any],
        solicitud_id: int | None = None,
    ) -> Solicitud:
        return Solicitud(
            id=solicitud_id,
            titulo=datos["titulo"].strip(),
            area_solicitante=(
                datos["area_solicitante"].strip()
            ),
            prioridad=datos["prioridad"],
            costo_estimado=Decimal(
                str(datos["costo_estimado"])
            ),
            estado=datos["estado"],
        )

    @staticmethod
    def _crear_respuesta_error(
        error: ApplicationException,
    ) -> Response:
        status_code = (
            SolicitudController._obtener_codigo_http(error)
        )

        return (
            {
                "error": error.to_dict(),
            },
            status_code,
        )

    @staticmethod
    def _obtener_codigo_http(
        error: ApplicationException,
    ) -> int:
        if isinstance(error, ValidationException):
            return HTTPStatus.BAD_REQUEST

        if isinstance(error, SolicitudNotFoundException):
            return HTTPStatus.NOT_FOUND

        if isinstance(error, PersistenceException):
            return HTTPStatus.INTERNAL_SERVER_ERROR

        return HTTPStatus.INTERNAL_SERVER_ERROR

    @staticmethod
    def _crear_error_interno() -> Response:
        return (
            {
                "error": {
                    "code": "INTERNAL_SERVER_ERROR",
                    "message": (
                        "Ocurrió un error interno en el servidor."
                    ),
                }
            },
            HTTPStatus.INTERNAL_SERVER_ERROR,
        )