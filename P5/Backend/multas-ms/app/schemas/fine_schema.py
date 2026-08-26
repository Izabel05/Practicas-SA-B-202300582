from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, Field

from app.models.fine import Fine


class CreateFineRequest(BaseModel):
    id_prestamo: UUID
    id_usuario: UUID
    dias_atraso: int = Field(gt=0)
    fecha_generacion: datetime | None = None


class FineResponse(BaseModel):
    id_multa: UUID
    id_prestamo: UUID
    id_usuario: UUID
    monto: Decimal
    motivo: str
    estado: str
    fecha_generacion: datetime
    fecha_pago: datetime | None
    actualizado_en: datetime

    @classmethod
    def from_domain(cls, fine: Fine) -> "FineResponse":
        return cls(
            id_multa=fine.id,
            id_prestamo=fine.loan_id,
            id_usuario=fine.user_id,
            monto=fine.amount,
            motivo=fine.reason,
            estado=fine.status.value,
            fecha_generacion=fine.generated_at,
            fecha_pago=fine.paid_at,
            actualizado_en=fine.updated_at,
        )
