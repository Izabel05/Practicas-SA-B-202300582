from dataclasses import dataclass
from decimal import Decimal

@dataclass
class Solicitud:
    id: int | None
    titulo: str
    area_solicitante: str
    prioridad: int
    costo_estimado: Decimal
    estado: str

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "titulo": self.titulo,
            "area_solicitante": self.area_solicitante,
            "prioridad": self.prioridad,
            "costo_estimado": float(self.costo_estimado),
            "estado": self.estado,
        }