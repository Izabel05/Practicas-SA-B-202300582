from dataclasses import dataclass, field
from datetime import datetime
from enum import StrEnum
from uuid import UUID


class LoanStatus(StrEnum):
    ACTIVE = "ACTIVO"
    COMPLETED = "COMPLETADO"
    OVERDUE = "VENCIDO"


class DetailStatus(StrEnum):
    LOANED = "PRESTADO"
    RETURNED = "DEVUELTO"
    OVERDUE = "VENCIDO"


@dataclass(slots=True)
class LoanDetail:
    id: UUID
    loan_id: UUID
    copy_id: UUID
    return_date: datetime | None
    status: DetailStatus


@dataclass(slots=True)
class Loan:
    id: UUID
    user_id: UUID
    loan_date: datetime
    due_date: datetime
    status: LoanStatus
    created_at: datetime
    updated_at: datetime
    details: list[LoanDetail] = field(default_factory=list)
