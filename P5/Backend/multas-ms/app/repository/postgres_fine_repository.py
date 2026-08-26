from datetime import datetime
from uuid import UUID

from psycopg.rows import dict_row
from psycopg_pool import ConnectionPool

from app.models.errors import ConflictError, NotFoundError
from app.models.fine import Fine, FineStatus


class PostgresFineRepository:
    def __init__(self, pool: ConnectionPool) -> None:
        self._pool = pool

    def create_idempotent(self, fine: Fine) -> Fine:
        with self._pool.connection() as connection:
            with connection.cursor(row_factory=dict_row) as cursor:
                cursor.execute(
                    """
                    INSERT INTO multas (
                        id_multa, id_prestamo, id_usuario, monto, motivo,
                        estado, fecha_generacion, fecha_pago, actualizado_en
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, NULL, %s)
                    ON CONFLICT (id_prestamo) DO UPDATE
                    SET id_prestamo = EXCLUDED.id_prestamo
                    RETURNING *
                    """,
                    (
                        fine.id,
                        fine.loan_id,
                        fine.user_id,
                        fine.amount,
                        fine.reason,
                        fine.status.value,
                        fine.generated_at,
                        fine.updated_at,
                    ),
                )
                return self._from_row(cursor.fetchone())

    def find_by_id(self, fine_id: UUID) -> Fine:
        with self._pool.connection() as connection:
            with connection.cursor(row_factory=dict_row) as cursor:
                cursor.execute("SELECT * FROM multas WHERE id_multa = %s", (fine_id,))
                row = cursor.fetchone()
                if row is None:
                    raise NotFoundError("multa no encontrada")
                return self._from_row(row)

    def find_by_user(self, user_id: UUID) -> list[Fine]:
        with self._pool.connection() as connection:
            with connection.cursor(row_factory=dict_row) as cursor:
                cursor.execute(
                    "SELECT * FROM multas WHERE id_usuario = %s ORDER BY fecha_generacion DESC",
                    (user_id,),
                )
                return [self._from_row(row) for row in cursor.fetchall()]

    def mark_paid(self, fine_id: UUID, paid_at: datetime) -> Fine:
        with self._pool.connection() as connection:
            with connection.cursor(row_factory=dict_row) as cursor:
                cursor.execute(
                    """
                    UPDATE multas
                    SET estado = 'PAGADA', fecha_pago = %s, actualizado_en = CURRENT_TIMESTAMP
                    WHERE id_multa = %s AND estado = 'PENDIENTE'
                    RETURNING *
                    """,
                    (paid_at, fine_id),
                )
                row = cursor.fetchone()
                if row is not None:
                    return self._from_row(row)
                cursor.execute("SELECT EXISTS(SELECT 1 FROM multas WHERE id_multa = %s)", (fine_id,))
                if cursor.fetchone()["exists"]:
                    raise ConflictError("solamente una multa pendiente puede pagarse")
                raise NotFoundError("multa no encontrada")

    @staticmethod
    def _from_row(row: dict) -> Fine:
        return Fine(
            id=row["id_multa"],
            loan_id=row["id_prestamo"],
            user_id=row["id_usuario"],
            amount=row["monto"],
            reason=row["motivo"],
            status=FineStatus(row["estado"]),
            generated_at=row["fecha_generacion"],
            paid_at=row["fecha_pago"],
            updated_at=row["actualizado_en"],
        )
