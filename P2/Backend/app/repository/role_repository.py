from typing import Any

from psycopg import DatabaseError

from app.config.database import Database
from app.exceptions.database_exception import DatabaseOperationException
from app.models.role import Role, RoleName
from app.repository.interface.role_repository_interface import (
    RoleRepositoryInterface,
)


class RoleRepository(RoleRepositoryInterface):
    """Implementa las consultas de roles en PostgreSQL."""

    def __init__(self, database: Database) -> None:
        self._database = database

    def find_by_name(self, role_name: RoleName) -> Role | None:
        query = """
            SELECT
                id,
                nombre,
                descripcion
            FROM roles
            WHERE nombre = %s
            LIMIT 1;
        """

        try:
            with self._database.connection() as connection:
                with connection.cursor() as cursor:
                    cursor.execute(query, (role_name.value,))
                    row = cursor.fetchone()

            return self._map_role(row) if row else None

        except DatabaseError as error:
            raise DatabaseOperationException() from error

    @staticmethod
    def _map_role(row: dict[str, Any]) -> Role:
        return Role(
            id=row["id"],
            name=RoleName(row["nombre"]),
            description=row["descripcion"],
        )