import unittest
from datetime import datetime, timedelta, timezone
from uuid import uuid4

from app.models.errors import ExternalServiceError, InvalidInputError
from app.models.loan import DetailStatus, Loan, LoanDetail, LoanStatus
from app.service.loan_service import LoanService


class FakeRepository:
    def __init__(self) -> None:
        self.loan_id = uuid4()
        self.detail_id = uuid4()
        self.copy_id = uuid4()

    def create(self, user_id, due_date, copy_ids):
        now = datetime.now(timezone.utc)
        return Loan(
            self.loan_id,
            user_id,
            now,
            due_date,
            LoanStatus.ACTIVE,
            now,
            now,
            [LoanDetail(self.detail_id, self.loan_id, copy_ids[0], None, DetailStatus.LOANED)],
        )

    def find_by_id(self, loan_id):
        return self.create(uuid4(), datetime.now(timezone.utc) + timedelta(days=7), [self.copy_id])

    def find_by_user(self, user_id):
        return []

    def find_detail_by_id(self, detail_id):
        return LoanDetail(detail_id, self.loan_id, self.copy_id, None, DetailStatus.LOANED)

    def return_detail(self, detail_id, return_date):
        return LoanDetail(detail_id, self.loan_id, self.copy_id, return_date, DetailStatus.RETURNED)

    def find_overdue(self, current_time):
        return []

    def mark_overdue(self, loan_id):
        return self.find_by_id(loan_id)


class FakeCatalogClient:
    def __init__(self, fail: bool = False) -> None:
        self.fail = fail
        self.updates: list[tuple] = []

    def update_copy_status(self, copy_id, status):
        self.updates.append((copy_id, status))
        if self.fail:
            raise ExternalServiceError("Catálogo no disponible")


class FakeFineClient:
    def create_fine(self, loan, days_overdue):
        return None


class LoanServiceTests(unittest.TestCase):
    def test_create_loan_reserves_copy(self):
        repository = FakeRepository()
        catalog = FakeCatalogClient()
        service = LoanService(repository, catalog, FakeFineClient())
        user_id, copy_id = uuid4(), uuid4()

        loan = service.create_loan(
            user_id,
            [copy_id],
            datetime.now(timezone.utc) + timedelta(days=7),
        )

        self.assertEqual(LoanStatus.ACTIVE, loan.status)
        self.assertEqual([(copy_id, "PRESTADO")], catalog.updates)

    def test_create_loan_rejects_past_due_date(self):
        service = LoanService(FakeRepository(), FakeCatalogClient(), FakeFineClient())
        with self.assertRaises(InvalidInputError):
            service.create_loan(uuid4(), [uuid4()], datetime.now(timezone.utc) - timedelta(days=1))

    def test_return_copy_releases_catalog_copy(self):
        repository = FakeRepository()
        catalog = FakeCatalogClient()
        service = LoanService(repository, catalog, FakeFineClient())

        detail = service.return_copy(repository.detail_id)

        self.assertEqual(DetailStatus.RETURNED, detail.status)
        self.assertEqual([(repository.copy_id, "DISPONIBLE")], catalog.updates)


if __name__ == "__main__":
    unittest.main()
