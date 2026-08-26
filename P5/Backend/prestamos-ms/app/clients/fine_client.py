from datetime import datetime

import httpx

from app.models.errors import ExternalServiceError
from app.models.loan import Loan


class HttpFineClient:
    def __init__(self, base_url: str, timeout: float = 5.0) -> None:
        self._base_url = base_url.rstrip("/")
        self._timeout = timeout

    def create_fine(self, loan: Loan, days_overdue: int) -> None:
        try:
            response = httpx.post(
                f"{self._base_url}/api/v1/multas",
                json={
                    "id_prestamo": str(loan.id),
                    "id_usuario": str(loan.user_id),
                    "dias_atraso": days_overdue,
                    "fecha_generacion": datetime.now().astimezone().isoformat(),
                },
                timeout=self._timeout,
            )
            response.raise_for_status()
        except httpx.HTTPError as error:
            raise ExternalServiceError("no fue posible registrar la multa") from error
