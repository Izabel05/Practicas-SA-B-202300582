from app.exceptions import SolicitudNotFoundException
from app.models.sollicitud_model import Solicitud
from app.repositories.solicitud_repository_interface import (
    SolicitudRepositoryInterface,
)


class SolicitudService:
    """
    Gestiona los casos de uso relacionados con solicitudes
    operativas.
    """

    def __init__(
        self,
        repository: SolicitudRepositoryInterface,
    ) -> None:
        self._repository = repository

    def crear(self, solicitud: Solicitud) -> Solicitud:
        solicitud.id = None
        return self._repository.crear(solicitud)

    def obtener_todas(self) -> list[Solicitud]:
        return self._repository.obtener_todas()

    def obtener_por_id(self, solicitud_id: int) -> Solicitud:
        solicitud = self._repository.obtener_por_id(solicitud_id)

        if solicitud is None:
            raise SolicitudNotFoundException(solicitud_id)

        return solicitud

    def actualizar(self, solicitud: Solicitud) -> Solicitud:
        if solicitud.id is None:
            raise ValueError(
                "La solicitud necesita un identificador."
            )

        solicitud_actualizada = self._repository.actualizar(
            solicitud
        )

        if solicitud_actualizada is None:
            raise SolicitudNotFoundException(solicitud.id)

        return solicitud_actualizada

    def actualizar_estado(
        self,
        solicitud_id: int,
        estado: str,
    ) -> Solicitud:
        solicitud_actualizada = (
            self._repository.actualizar_estado(
                solicitud_id=solicitud_id,
                estado=estado,
            )
        )

        if solicitud_actualizada is None:
            raise SolicitudNotFoundException(solicitud_id)

        return solicitud_actualizada

    def eliminar(self, solicitud_id: int) -> None:
        solicitud_eliminada = self._repository.eliminar(
            solicitud_id
        )

        if not solicitud_eliminada:
            raise SolicitudNotFoundException(solicitud_id)