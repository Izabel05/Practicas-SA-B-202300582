from collections.abc import Callable

from psycopg import Connection, connect
from psycopg.errors import OperationalError

from app.config.settings import Settings


ConnectionFactory = Callable[[], Connection]


def get_connection() -> Connection:
    """
    Crea y devuelve una nueva conexión a PostgreSQL en NeonDB.

    La conexión real se verifica al ejecutar connect().
    """
    return connect(
        conninfo=Settings.DATABASE_URL,
        autocommit=False,
    )


def verify_database_connection() -> None:
    """
    Comprueba que la aplicación pueda conectarse correctamente
    a PostgreSQL.

    Debe utilizarse al iniciar la aplicación, no antes de cada
    operación del repositorio.
    """
    try:
        with get_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1;")
                cursor.fetchone()

    except OperationalError as error:
        raise RuntimeError(
            "No fue posible establecer conexión con NeonDB."
        ) from error