from uuid import UUID

from fastapi import APIRouter, Depends, Request, status

from app.schemas.fine_schema import CreateFineRequest, FineResponse
from app.service.fine_service import FineService

router = APIRouter(prefix="/api/v1")


def fine_service(request: Request) -> FineService:
    return request.app.state.fine_service


@router.post("/multas", response_model=FineResponse, status_code=status.HTTP_201_CREATED)
def create_fine(
    request: CreateFineRequest,
    service: FineService = Depends(fine_service),
) -> FineResponse:
    fine = service.create_for_overdue_loan(
        request.id_prestamo,
        request.id_usuario,
        request.dias_atraso,
        request.fecha_generacion,
    )
    return FineResponse.from_domain(fine)


@router.get("/multas/{fine_id}", response_model=FineResponse)
def find_fine(fine_id: UUID, service: FineService = Depends(fine_service)) -> FineResponse:
    return FineResponse.from_domain(service.find_fine(fine_id))


@router.get("/usuarios/{user_id}/multas", response_model=list[FineResponse])
def find_user_fines(user_id: UUID, service: FineService = Depends(fine_service)) -> list[FineResponse]:
    return [FineResponse.from_domain(fine) for fine in service.find_user_fines(user_id)]


@router.patch("/multas/{fine_id}/pagar", response_model=FineResponse)
def pay_fine(fine_id: UUID, service: FineService = Depends(fine_service)) -> FineResponse:
    return FineResponse.from_domain(service.pay_fine(fine_id))
