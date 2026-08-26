from datetime import datetime, timezone
from decimal import Decimal, ROUND_HALF_UP
from uuid import UUID, uuid4

from app.models.errors import InvalidInputError
from app.models.fine import Fine, FineStatus
from app.repository.interfaces import FineRepository


class FineService:
    def __init__(self, repository: FineRepository, daily_rate: Decimal) -> None:
        if daily_rate <= 0:
            raise ValueError("la tarifa diaria debe ser positiva")
        self._repository = repository
        self._daily_rate = daily_rate

    def create_for_overdue_loan(
        self,
        loan_id: UUID,
        user_id: UUID,
        days_overdue: int,
        generated_at: datetime | None = None,
    ) -> Fine:
        if days_overdue <= 0:
            raise InvalidInputError("dias_atraso debe ser mayor que cero")
        now = generated_at or datetime.now(timezone.utc)
        amount = (self._daily_rate * days_overdue).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        fine = Fine(
            id=uuid4(),
            loan_id=loan_id,
            user_id=user_id,
            amount=amount,
            reason=f"Préstamo vencido por {days_overdue} día(s)",
            status=FineStatus.PENDING,
            generated_at=now,
            paid_at=None,
            updated_at=now,
        )
        return self._repository.create_idempotent(fine)

    def find_fine(self, fine_id: UUID) -> Fine:
        return self._repository.find_by_id(fine_id)

    def find_user_fines(self, user_id: UUID) -> list[Fine]:
        return self._repository.find_by_user(user_id)

    def pay_fine(self, fine_id: UUID) -> Fine:
        return self._repository.mark_paid(fine_id, datetime.now(timezone.utc))
