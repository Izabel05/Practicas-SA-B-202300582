from datetime import datetime, timezone
from uuid import UUID

from app.models.errors import ConflictError, InvalidInputError
from app.models.loan import Loan, LoanDetail
from app.repository.interfaces import CatalogClient, FineClient, LoanRepository


class LoanService:
    def __init__(
        self,
        repository: LoanRepository,
        catalog_client: CatalogClient,
        fine_client: FineClient,
    ) -> None:
        self._repository = repository
        self._catalog = catalog_client
        self._fines = fine_client

    def create_loan(self, user_id: UUID, copy_ids: list[UUID], due_date: datetime) -> Loan:
        now = datetime.now(timezone.utc)
        if not copy_ids or len(set(copy_ids)) != len(copy_ids) or due_date <= now:
            raise InvalidInputError("usuario, ejemplares únicos y fecha límite futura son obligatorios")

        reserved: list[UUID] = []
        try:
            for copy_id in copy_ids:
                self._catalog.update_copy_status(copy_id, "PRESTADO")
                reserved.append(copy_id)
            return self._repository.create(user_id, due_date, copy_ids)
        except Exception:
            for copy_id in reserved:
                try:
                    self._catalog.update_copy_status(copy_id, "DISPONIBLE")
                except Exception:
                    pass
            raise

    def find_loan(self, loan_id: UUID) -> Loan:
        return self._repository.find_by_id(loan_id)

    def find_user_loans(self, user_id: UUID) -> list[Loan]:
        return self._repository.find_by_user(user_id)

    def return_copy(self, detail_id: UUID) -> LoanDetail:
        detail = self._find_detail(detail_id)
        if detail.status.value == "DEVUELTO":
            raise ConflictError("el ejemplar ya fue devuelto")

        self._catalog.update_copy_status(detail.copy_id, "DISPONIBLE")
        try:
            return self._repository.return_detail(detail_id, datetime.now(timezone.utc))
        except Exception:
            try:
                self._catalog.update_copy_status(detail.copy_id, "PRESTADO")
            except Exception:
                pass
            raise

    def process_overdue(self) -> list[Loan]:
        now = datetime.now(timezone.utc)
        processed: list[Loan] = []
        for loan in self._repository.find_overdue(now):
            days_overdue = max(1, (now.date() - loan.due_date.date()).days)
            self._fines.create_fine(loan, days_overdue)
            processed.append(self._repository.mark_overdue(loan.id))
        return processed

    def _find_detail(self, detail_id: UUID) -> LoanDetail:
        if not detail_id:
            raise InvalidInputError("id_detalle es obligatorio")
        return self._repository.find_detail_by_id(detail_id)
