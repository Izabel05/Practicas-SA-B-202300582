from datetime import datetime
from uuid import UUID

import strawberry
from strawberry.types import Info

from app.models.loan import Loan, LoanDetail
from app.service.loan_service import LoanService


@strawberry.type
class LoanDetailType:
    id_detalle: UUID
    id_prestamo: UUID
    id_ejemplar: UUID
    fecha_devolucion: datetime | None
    estado: str


@strawberry.type
class LoanType:
    id_prestamo: UUID
    id_usuario: UUID
    fecha_prestamo: datetime
    fecha_limite: datetime
    estado: str
    fecha_creacion: datetime
    actualizado_en: datetime
    detalles: list[LoanDetailType]


def detail_type(detail: LoanDetail) -> LoanDetailType:
    return LoanDetailType(
        id_detalle=detail.id,
        id_prestamo=detail.loan_id,
        id_ejemplar=detail.copy_id,
        fecha_devolucion=detail.return_date,
        estado=detail.status.value,
    )


def loan_type(loan: Loan) -> LoanType:
    return LoanType(
        id_prestamo=loan.id,
        id_usuario=loan.user_id,
        fecha_prestamo=loan.loan_date,
        fecha_limite=loan.due_date,
        estado=loan.status.value,
        fecha_creacion=loan.created_at,
        actualizado_en=loan.updated_at,
        detalles=[detail_type(detail) for detail in loan.details],
    )


def get_service(info: Info) -> LoanService:
    return info.context["loan_service"]


@strawberry.type
class Query:
    @strawberry.field
    def prestamo(self, info: Info, id: UUID) -> LoanType:
        return loan_type(get_service(info).find_loan(id))

    @strawberry.field
    def prestamos_por_usuario(self, info: Info, id_usuario: UUID) -> list[LoanType]:
        return [loan_type(loan) for loan in get_service(info).find_user_loans(id_usuario)]


@strawberry.type
class Mutation:
    @strawberry.mutation
    def crear_prestamo(
        self,
        info: Info,
        id_usuario: UUID,
        ids_ejemplares: list[UUID],
        fecha_limite: datetime,
    ) -> LoanType:
        return loan_type(get_service(info).create_loan(id_usuario, ids_ejemplares, fecha_limite))

    @strawberry.mutation
    def devolver_ejemplar(self, info: Info, id_detalle: UUID) -> LoanDetailType:
        return detail_type(get_service(info).return_copy(id_detalle))


schema = strawberry.Schema(query=Query, mutation=Mutation)
