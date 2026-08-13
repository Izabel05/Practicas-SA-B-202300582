from typing import Any
from uuid import UUID

from psycopg import DatabaseError
from psycopg.errors import UniqueViolation

from app.config.database import Database
from app.exceptions.database_exception import DatabaseOperationException
from app.exceptions.user_exceptions import (
    UserAlreadyExistsException,
    UserCreationException,
)
from app.models.role import RoleName
from app.models.user import User
from app.repository.interface.user_repository_interface import (
    UserRepositoryInterface,
)
from app.service.data_encryption_service import DataEncryptionService


class UserRepository(UserRepositoryInterface):
    """Implementa las operaciones de usuarios en PostgreSQL."""

    def __init__(
        self,
        database: Database,
        encryption_service: DataEncryptionService,
    ) -> None:
        self._database = database
        self._encryption_service = encryption_service

    def find_by_email(self, email: str) -> User | None:
        query = """
            SELECT
                u.id,
                u.nombre AS first_name,
                u.apellido AS last_name,
                u.correo AS email,
                u.password_hash,
                u.rol_id AS role_id,
                r.nombre AS role_name,
                u.activo AS is_active,
                u.correo_verificado AS email_verified,
                u.ultimo_acceso AS last_login,
                u.creado_en AS created_at,
                u.actualizado_en AS updated_at
            FROM usuarios AS u
            INNER JOIN roles AS r
                ON r.id = u.rol_id
            WHERE u.correo_hash = %s
            LIMIT 1;
        """

        try:
            with self._database.connection() as connection:
                with connection.cursor() as cursor:
                    cursor.execute(
                        query,
                        (self._encryption_service.create_search_hash(email),),
                    )
                    row = cursor.fetchone()

            return self._map_user(row) if row else None

        except DatabaseError as error:
            raise DatabaseOperationException() from error

    def find_by_id(self, user_id: UUID) -> User | None:
        query = """
            SELECT
                u.id,
                u.nombre AS first_name,
                u.apellido AS last_name,
                u.correo AS email,
                u.password_hash,
                u.rol_id AS role_id,
                r.nombre AS role_name,
                u.activo AS is_active,
                u.correo_verificado AS email_verified,
                u.ultimo_acceso AS last_login,
                u.creado_en AS created_at,
                u.actualizado_en AS updated_at
            FROM usuarios AS u
            INNER JOIN roles AS r
                ON r.id = u.rol_id
            WHERE u.id = %s
            LIMIT 1;
        """

        try:
            with self._database.connection() as connection:
                with connection.cursor() as cursor:
                    cursor.execute(query, (user_id,))
                    row = cursor.fetchone()

            return self._map_user(row) if row else None

        except DatabaseError as error:
            raise DatabaseOperationException() from error

    def create(
        self,
        first_name: str,
        last_name: str,
        email: str,
        password_hash: str,
        role_id: int,
    ) -> User:
        query = """
            INSERT INTO usuarios (
                nombre,
                apellido,
                correo,
                correo_hash,
                password_hash,
                rol_id
            )
            VALUES (%s, %s, %s, %s, %s, %s)
            RETURNING id;
        """

        try:
            with self._database.connection() as connection:
                with connection.cursor() as cursor:
                    cursor.execute(
                        query,
                        (
                            self._encryption_service.encrypt(first_name),
                            self._encryption_service.encrypt(last_name),
                            self._encryption_service.encrypt(email),
                            self._encryption_service.create_search_hash(email),
                            password_hash,
                            role_id,
                        ),
                    )
                    row = cursor.fetchone()

            if not row:
                raise UserCreationException()

            user = self.find_by_id(row["id"])

            if user is None:
                raise UserCreationException()

            return user

        except UniqueViolation as error:
            raise UserAlreadyExistsException() from error

        except UserCreationException:
            raise

        except DatabaseError as error:
            raise DatabaseOperationException() from error

    def update_last_login(self, user_id: UUID) -> None:
        query = """
            UPDATE usuarios
            SET ultimo_acceso = CURRENT_TIMESTAMP
            WHERE id = %s;
        """

        try:
            with self._database.connection() as connection:
                with connection.cursor() as cursor:
                    cursor.execute(query, (user_id,))

        except DatabaseError as error:
            raise DatabaseOperationException() from error

    def _map_user(self, row: dict[str, Any]) -> User:
        return User(
            id=row["id"],
            first_name=self._encryption_service.decrypt(row["first_name"]),
            last_name=self._encryption_service.decrypt(row["last_name"]),
            email=self._encryption_service.decrypt(row["email"]),
            password_hash=row["password_hash"],
            role_id=row["role_id"],
            role_name=RoleName(row["role_name"]),
            is_active=row["is_active"],
            email_verified=row["email_verified"],
            last_login=row["last_login"],
            created_at=row["created_at"],
            updated_at=row["updated_at"],
        )
