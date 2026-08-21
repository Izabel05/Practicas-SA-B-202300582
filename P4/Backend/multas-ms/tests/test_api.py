import unittest
from decimal import Decimal
from uuid import uuid4

from fastapi.testclient import TestClient

from app.main import create_app
from app.service.fine_service import FineService
from tests.test_fine_service import FakeFineRepository


class FineAPITests(unittest.TestCase):
    def test_create_and_query_fine(self):
        service = FineService(FakeFineRepository(), Decimal("5.00"))
        app = create_app(fine_service=service)
        loan_id, user_id = uuid4(), uuid4()

        with TestClient(app) as client:
            created = client.post(
                "/api/v1/multas",
                json={
                    "id_prestamo": str(loan_id),
                    "id_usuario": str(user_id),
                    "dias_atraso": 4,
                },
            )
            self.assertEqual(201, created.status_code, created.text)
            payload = created.json()
            queried = client.get(f"/api/v1/multas/{payload['id_multa']}")

        self.assertEqual(200, queried.status_code)
        self.assertEqual("20.00", queried.json()["monto"])
        self.assertEqual("PENDIENTE", queried.json()["estado"])

    def test_rejects_zero_overdue_days(self):
        service = FineService(FakeFineRepository(), Decimal("5.00"))
        app = create_app(fine_service=service)
        with TestClient(app) as client:
            response = client.post(
                "/api/v1/multas",
                json={
                    "id_prestamo": str(uuid4()),
                    "id_usuario": str(uuid4()),
                    "dias_atraso": 0,
                },
            )
        self.assertEqual(422, response.status_code)


if __name__ == "__main__":
    unittest.main()
