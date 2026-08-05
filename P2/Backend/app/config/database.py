from collections.abc import Generator
from contextlib import contextmanager

from psycopg import Connection
from psycopg.rows import dict_row
from psycopg_pool import ConnectionPool

from app.config.settings import Settings
from app.exceptions.database_exception import (
    DatabaseConnectionException,
)


class Database:
    """Administra el grupo de conexiones con PostgreSQL."""

    def __init__(self) -> None:
        Settings.validate()

        self._pool = ConnectionPool(
            conninfo=Settings.DATABASE_URL,
            min_size=Settings.DATABASE_POOL_MIN_SIZE,
            max_size=Settings.DATABASE_POOL_MAX_SIZE,
            kwargs={
                "autocommit": False,
                "row_factory": dict_row,
            },
            open=False,
        )

    def open(self) -> None:
        """Abre el grupo de conexiones."""

        try:
            self._pool.open()
            self._pool.wait()
        except Exception as error:
            raise DatabaseConnectionException() from error

    def close(self) -> None:
        """Cierra el grupo de conexiones."""

        self._pool.close()

    @contextmanager
    def connection(
        self,
    ) -> Generator[Connection, None, None]:
        """Entrega una conexión con control de transacciones."""

        try:
            with self._pool.connection() as connection:
                try:
                    yield connection
                    connection.commit()
                except Exception:
                    connection.rollback()
                    raise
        except DatabaseConnectionException:
            raise
        except Exception as error:
            raise DatabaseConnectionException() from error

    def health_check(self) -> bool:
        """Comprueba la comunicación con PostgreSQL."""

        try:
            with self.connection() as connection:
                with connection.cursor() as cursor:
                    cursor.execute("SELECT 1 AS status;")
                    result = cursor.fetchone()

            return bool(result and result["status"] == 1)

        except DatabaseConnectionException:
            return False