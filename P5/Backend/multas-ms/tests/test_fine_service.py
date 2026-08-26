import unittest
from dataclasses import replace
from datetime import datetime, timezone
from decimal import Decimal
from uuid import uuid4

from app.models.errors import NotFoundError
from app.models.fine import FineStatus
from app.service.fine_service import FineService


class FakeFineRepository:
    def __init__(self) -> None:
        self.by_id = {}
        self.by_loan = {}

    def create_idempotent(self, fine):
        if fine.loan_id in self.by_loan:
            return self.by_loan[fine.loan_id]
        self.by_id[fine.id] = fine
        self.by_loan[fine.loan_id] = fine
        return fine

    def find_by_id(self, fine_id):
        try:
            return self.by_id[fine_id]
        except KeyError as error:
            raise NotFoundError("multa no encontrada") from error

    def find_by_user(self, user_id):
        return [fine for fine in self.by_id.values() if fine.user_id == user_id]

    def mark_paid(self, fine_id, paid_at):
        fine = self.find_by_id(fine_id)
        paid = replace(fine, status=FineStatus.PAID, paid_at=paid_at, updated_at=paid_at)
        self.by_id[fine_id] = paid
        self.by_loan[paid.loan_id] = paid
        return paid


class FineServiceTests(unittest.TestCase):
    def test_calculates_amount_by_overdue_days(self):
        service = FineService(FakeFineRepository(), Decimal("5.00"))

        fine = service.create_for_overdue_loan(
            uuid4(),
            uuid4(),
            3,
            datetime.now(timezone.utc),
        )

        self.assertEqual(Decimal("15.00"), fine.amount)
        self.assertEqual(FineStatus.PENDING, fine.status)

    def test_creation_is_idempotent_by_loan(self):
        service = FineService(FakeFineRepository(), Decimal("5.00"))
        loan_id, user_id = uuid4(), uuid4()

        first = service.create_for_overdue_loan(loan_id, user_id, 2)
        second = service.create_for_overdue_loan(loan_id, user_id, 2)

        self.assertEqual(first.id, second.id)

    def test_marks_pending_fine_as_paid(self):
        service = FineService(FakeFineRepository(), Decimal("5.00"))
        fine = service.create_for_overdue_loan(uuid4(), uuid4(), 1)

        paid = service.pay_fine(fine.id)

        self.assertEqual(FineStatus.PAID, paid.status)
        self.assertIsNotNone(paid.paid_at)


if __name__ == "__main__":
    unittest.main()
