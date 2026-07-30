from collections.abc import Callable
from typing import Any

from psycopg import Connection
from psycopg.rows import dict_row
from psycopg import Error as PsycopgError

from app.exceptions import PersistenceException
from app.models.sollicitud_model import Solicitud
from app.repositories.solicitud_repository_interface import (
    SolicitudRepositoryInterface,
)


ConnectionFactory = Callable[[], Connection]


class SolicitudRepository(SolicitudRepositoryInterface):
    """
    Implementa las operaciones CRUD de la tabla solicitudes
    utilizando PostgreSQL.
    """

    def __init__(
        self,
        connection_factory: ConnectionFactory,
    ) -> None:
        self._connection_factory = connection_factory

    def crear(self, solicitud: Solicitud) -> Solicitud:
        consulta = """
            INSERT INTO solicitudes (
                titulo,
                area_solicitante,
                prioridad,
                costo_estimado,
                estado
            )
            VALUES (
                %(titulo)s,
                %(area_solicitante)s,
                %(prioridad)s,
                %(costo_estimado)s,
                %(estado)s
            )
            RETURNING
                id,
                titulo,
                area_solicitante,
                prioridad,
                costo_estimado,
                estado;
        """

        parametros = self._crear_parametros(solicitud)

        with self._connection_factory() as conexion:
            with conexion.cursor(row_factory=dict_row) as cursor:
                cursor.execute(consulta, parametros)
                fila = cursor.fetchone()

        if fila is None:
            raise RuntimeError(
                "La base de datos no devolvió la solicitud creada."
            )

        return self._convertir_fila_en_solicitud(fila)

    def obtener_todas(self) -> list[Solicitud]:
        consulta = """
            SELECT
                id,
                titulo,
                area_solicitante,
                prioridad,
                costo_estimado,
                estado
            FROM solicitudes
            ORDER BY fecha_creacion DESC, id DESC;
        """

        with self._connection_factory() as conexion:
            with conexion.cursor(row_factory=dict_row) as cursor:
                cursor.execute(consulta)
                filas = cursor.fetchall()

        return [
            self._convertir_fila_en_solicitud(fila)
            for fila in filas
        ]

    def obtener_por_id(
        self,
        solicitud_id: int,
    ) -> Solicitud | None:
        consulta = """
            SELECT
                id,
                titulo,
                area_solicitante,
                prioridad,
                costo_estimado,
                estado
            FROM solicitudes
            WHERE id = %s;
        """

        with self._connection_factory() as conexion:
            with conexion.cursor(row_factory=dict_row) as cursor:
                cursor.execute(consulta, (solicitud_id,))
                fila = cursor.fetchone()

        if fila is None:
            return None

        return self._convertir_fila_en_solicitud(fila)

    def actualizar(
        self,
        solicitud: Solicitud,
    ) -> Solicitud | None:
        if solicitud.id is None:
            raise ValueError(
                "La solicitud debe tener un id para ser actualizada."
            )

        consulta = """
            UPDATE solicitudes
            SET
                titulo = %(titulo)s,
                area_solicitante = %(area_solicitante)s,
                prioridad = %(prioridad)s,
                costo_estimado = %(costo_estimado)s,
                estado = %(estado)s,
                fecha_actualizacion = CURRENT_TIMESTAMP
            WHERE id = %(id)s
            RETURNING
                id,
                titulo,
                area_solicitante,
                prioridad,
                costo_estimado,
                estado;
        """

        parametros = {
            "id": solicitud.id,
            **self._crear_parametros(solicitud),
        }

        with self._connection_factory() as conexion:
            with conexion.cursor(row_factory=dict_row) as cursor:
                cursor.execute(consulta, parametros)
                fila = cursor.fetchone()

        if fila is None:
            return None

        return self._convertir_fila_en_solicitud(fila)

    def eliminar(self, solicitud_id: int) -> bool:
        consulta = """
            DELETE FROM solicitudes
            WHERE id = %s
            RETURNING id;
        """

        with self._connection_factory() as conexion:
            with conexion.cursor() as cursor:
                cursor.execute(consulta, (solicitud_id,))
                fila_eliminada = cursor.fetchone()

        return fila_eliminada is not None
    def actualizar_estado(
        self,
        solicitud_id: int,
        estado: str,
    ) -> Solicitud | None:
        query = """
            UPDATE solicitudes
            SET
                estado = %s,
                fecha_actualizacion = CURRENT_TIMESTAMP
            WHERE id = %s
            RETURNING
                id,
                titulo,
                area_solicitante,
                prioridad,
                costo_estimado,
                estado;
        """

        parametros = (
            estado,
            solicitud_id,
        )

        try:
            with self._connection_factory() as connection:
                with connection.cursor(
                    row_factory=dict_row
                ) as cursor:
                    cursor.execute(query, parametros)
                    fila = cursor.fetchone()

                    if fila is None:
                        return None

                    return self._convertir_fila_en_solicitud(fila)

        except PsycopgError as error:
            raise PersistenceException(
                operation="actualizar estado de solicitud"
            ) from error
        
    @staticmethod
    def _crear_parametros(
        solicitud: Solicitud,
    ) -> dict[str, Any]:
        """
        Convierte el modelo en parámetros para las consultas SQL.
        """
        return {
            "titulo": solicitud.titulo,
            "area_solicitante": solicitud.area_solicitante,
            "prioridad": solicitud.prioridad,
            "costo_estimado": solicitud.costo_estimado,
            "estado": solicitud.estado,
        }

    @staticmethod
    def _convertir_fila_en_solicitud(
        fila: dict[str, Any],
    ) -> Solicitud:
        """
        Convierte una fila de PostgreSQL en una instancia
        del modelo Solicitud.
        """
        return Solicitud(
            id=fila["id"],
            titulo=fila["titulo"],
            area_solicitante=fila["area_solicitante"],
            prioridad=fila["prioridad"],
            costo_estimado=fila["costo_estimado"],
            estado=fila["estado"],
        )