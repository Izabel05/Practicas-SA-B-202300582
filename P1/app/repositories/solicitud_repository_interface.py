from abc import ABC, abstractmethod
from app.models.sollicitud_model import Solicitud


class SolicitudRepositoryInterface(ABC):
    """
    Define el contrato de persistencia para las solicitudes.
    """

    @abstractmethod
    def crear(self, solicitud: Solicitud) -> Solicitud:
        pass

    @abstractmethod
    def obtener_todas(self) -> list[Solicitud]:
        pass

    @abstractmethod
    def obtener_por_id(
        self,
        solicitud_id: int,
    ) -> Solicitud | None:
        pass

    @abstractmethod
    def actualizar(
        self,
        solicitud: Solicitud,
    ) -> Solicitud | None:
        pass

    @abstractmethod
    def actualizar_estado(
        self,
        solicitud_id: int,
        estado: str,
    ) -> Solicitud | None:
        pass

    @abstractmethod
    def eliminar(
        self,
        solicitud_id: int,
    ) -> bool:
        pass