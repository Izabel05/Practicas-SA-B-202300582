import unittest
from datetime import datetime, timedelta, timezone
from uuid import uuid4

from fastapi.testclient import TestClient

from app.main import create_app
from app.models.loan import DetailStatus, Loan, LoanDetail, LoanStatus


class FakeLoanService:
    def __init__(self) -> None:
        now = datetime.now(timezone.utc)
        loan_id, detail_id, copy_id = uuid4(), uuid4(), uuid4()
        self.loan = Loan(
            loan_id,
            uuid4(),
            now,
            now + timedelta(days=7),
            LoanStatus.ACTIVE,
            now,
            now,
            [LoanDetail(detail_id, loan_id, copy_id, None, DetailStatus.LOANED)],
        )

    def find_loan(self, loan_id):
        return self.loan

    def find_user_loans(self, user_id):
        return [self.loan]

    def create_loan(self, user_id, copy_ids, due_date):
        return self.loan

    def return_copy(self, detail_id):
        return self.loan.details[0]

    def process_overdue(self):
        return []


class GraphQLTests(unittest.TestCase):
    def test_query_loan(self):
        service = FakeLoanService()
        app = create_app(loan_service=service)
        with TestClient(app) as client:
            response = client.post(
                "/graphql",
                json={
                    "query": "query($id: UUID!) { prestamo(id: $id) { idPrestamo estado detalles { estado } } }",
                    "variables": {"id": str(service.loan.id)},
                },
            )

        self.assertEqual(200, response.status_code)
        payload = response.json()
        self.assertNotIn("errors", payload)
        self.assertEqual("ACTIVO", payload["data"]["prestamo"]["estado"])


if __name__ == "__main__":
    unittest.main()
