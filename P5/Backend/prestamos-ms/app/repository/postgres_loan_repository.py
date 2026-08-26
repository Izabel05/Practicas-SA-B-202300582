from datetime import datetime
from uuid import UUID

from psycopg import errors
from psycopg.rows import dict_row
from psycopg_pool import ConnectionPool

from app.models.errors import ConflictError, InvalidInputError, NotFoundError
from app.models.loan import DetailStatus, Loan, LoanDetail, LoanStatus


class PostgresLoanRepository:
    def __init__(self, pool: ConnectionPool) -> None:
        self._pool = pool

    def create(self, user_id: UUID, due_date: datetime, copy_ids: list[UUID]) -> Loan:
        try:
            with self._pool.connection() as connection, connection.transaction():
                with connection.cursor(row_factory=dict_row) as cursor:
                    cursor.execute(
                        """
                        INSERT INTO prestamos (id_usuario, fecha_limite, estado)
                        VALUES (%s, %s, 'ACTIVO')
                        RETURNING id_prestamo
                        """,
                        (user_id, due_date),
                    )
                    loan_id = cursor.fetchone()["id_prestamo"]
                    cursor.executemany(
                        """
                        INSERT INTO detalle_prestamo (id_prestamo, id_ejemplar, estado)
                        VALUES (%s, %s, 'PRESTADO')
                        """,
                        [(loan_id, copy_id) for copy_id in copy_ids],
                    )
            return self.find_by_id(loan_id)
        except errors.UniqueViolation as error:
            raise ConflictError("uno de los ejemplares ya tiene un préstamo activo") from error
        except (errors.ForeignKeyViolation, errors.InvalidTextRepresentation) as error:
            raise InvalidInputError("identificador inválido") from error

    def find_by_id(self, loan_id: UUID) -> Loan:
        with self._pool.connection() as connection:
            with connection.cursor(row_factory=dict_row) as cursor:
                cursor.execute("SELECT * FROM prestamos WHERE id_prestamo = %s", (loan_id,))
                row = cursor.fetchone()
                if row is None:
                    raise NotFoundError("préstamo no encontrado")
                loan = self._loan_from_row(row)
                loan.details = self._load_details(cursor, loan.id)
                return loan

    def find_by_user(self, user_id: UUID) -> list[Loan]:
        with self._pool.connection() as connection:
            with connection.cursor(row_factory=dict_row) as cursor:
                cursor.execute(
                    "SELECT * FROM prestamos WHERE id_usuario = %s ORDER BY fecha_prestamo DESC",
                    (user_id,),
                )
                loans = [self._loan_from_row(row) for row in cursor.fetchall()]
                for loan in loans:
                    loan.details = self._load_details(cursor, loan.id)
                return loans

    def find_detail_by_id(self, detail_id: UUID) -> LoanDetail:
        with self._pool.connection() as connection:
            with connection.cursor(row_factory=dict_row) as cursor:
                cursor.execute(
                    "SELECT * FROM detalle_prestamo WHERE id_detalle = %s",
                    (detail_id,),
                )
                row = cursor.fetchone()
                if row is None:
                    raise NotFoundError("detalle de préstamo no encontrado")
                return self._detail_from_row(row)

    def return_detail(self, detail_id: UUID, return_date: datetime) -> LoanDetail:
        with self._pool.connection() as connection, connection.transaction():
            with connection.cursor(row_factory=dict_row) as cursor:
                cursor.execute(
                    """
                    UPDATE detalle_prestamo
                    SET estado = 'DEVUELTO', fecha_devolucion = %s
                    WHERE id_detalle = %s AND estado IN ('PRESTADO', 'VENCIDO')
                    RETURNING *
                    """,
                    (return_date, detail_id),
                )
                row = cursor.fetchone()
                if row is None:
                    raise NotFoundError("detalle activo no encontrado")
                detail = self._detail_from_row(row)
                cursor.execute(
                    """
                    UPDATE prestamos
                    SET estado = 'COMPLETADO', actualizado_en = CURRENT_TIMESTAMP
                    WHERE id_prestamo = %s
                      AND NOT EXISTS (
                        SELECT 1 FROM detalle_prestamo
                        WHERE id_prestamo = %s AND estado <> 'DEVUELTO'
                      )
                    """,
                    (detail.loan_id, detail.loan_id),
                )
                return detail

    def find_overdue(self, current_time: datetime) -> list[Loan]:
        with self._pool.connection() as connection:
            with connection.cursor(row_factory=dict_row) as cursor:
                cursor.execute(
                    "SELECT * FROM prestamos WHERE estado = 'ACTIVO' AND fecha_limite < %s",
                    (current_time,),
                )
                loans = [self._loan_from_row(row) for row in cursor.fetchall()]
                for loan in loans:
                    loan.details = self._load_details(cursor, loan.id)
                return loans

    def mark_overdue(self, loan_id: UUID) -> Loan:
        with self._pool.connection() as connection, connection.transaction():
            with connection.cursor() as cursor:
                cursor.execute(
                    "UPDATE prestamos SET estado = 'VENCIDO', actualizado_en = CURRENT_TIMESTAMP WHERE id_prestamo = %s",
                    (loan_id,),
                )
                cursor.execute(
                    "UPDATE detalle_prestamo SET estado = 'VENCIDO' WHERE id_prestamo = %s AND estado = 'PRESTADO'",
                    (loan_id,),
                )
        return self.find_by_id(loan_id)

    @staticmethod
    def _load_details(cursor, loan_id: UUID) -> list[LoanDetail]:
        cursor.execute(
            "SELECT * FROM detalle_prestamo WHERE id_prestamo = %s ORDER BY id_detalle",
            (loan_id,),
        )
        return [PostgresLoanRepository._detail_from_row(row) for row in cursor.fetchall()]

    @staticmethod
    def _loan_from_row(row: dict) -> Loan:
        return Loan(
            id=row["id_prestamo"],
            user_id=row["id_usuario"],
            loan_date=row["fecha_prestamo"],
            due_date=row["fecha_limite"],
            status=LoanStatus(row["estado"]),
            created_at=row["fecha_creacion"],
            updated_at=row["actualizado_en"],
        )

    @staticmethod
    def _detail_from_row(row: dict) -> LoanDetail:
        return LoanDetail(
            id=row["id_detalle"],
            loan_id=row["id_prestamo"],
            copy_id=row["id_ejemplar"],
            return_date=row["fecha_devolucion"],
            status=DetailStatus(row["estado"]),
        )
