from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from enum import StrEnum
from uuid import UUID


class FineStatus(StrEnum):
    PENDING = "PENDIENTE"
    PAID = "PAGADA"
    CANCELLED = "ANULADA"


@dataclass(frozen=True, slots=True)
class Fine:
    id: UUID
    loan_id: UUID
    user_id: UUID
    amount: Decimal
    reason: str
    status: FineStatus
    generated_at: datetime
    paid_at: datetime | None
    updated_at: datetime
