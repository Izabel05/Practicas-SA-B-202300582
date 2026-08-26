from fastapi import APIRouter, Depends, Request

from app.controller.graphql_controller import LoanType, loan_type
from app.service.loan_service import LoanService

router = APIRouter()


def loan_service(request: Request) -> LoanService:
    return request.app.state.loan_service


@router.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "servicio": "prestamos-ms"}


@router.post("/api/v1/prestamos/procesar-vencidos", response_model=None)
def process_overdue(service: LoanService = Depends(loan_service)) -> list[LoanType]:
    return [loan_type(loan) for loan in service.process_overdue()]
