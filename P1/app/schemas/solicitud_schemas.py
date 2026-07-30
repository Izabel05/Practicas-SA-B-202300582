#valida los datos de netrada y de salida
from decimal import Decimal, InvalidOperation
from typing import Any


ESTADOS_PERMITIDOS = {
    "registrada",
    "en_proceso",
    "finalizada",
    "cancelada",
}

CAMPOS_SOLICITUD = {
    "titulo",
    "area_solicitante",
    "prioridad",
    "costo_estimado",
    "estado",
}


def validar_solicitud(datos: dict[str, Any]) -> dict[str, str]:
    """
    Valida todos los datos necesarios para crear o reemplazar
    completamente una solicitud.
    """
    errores: dict[str, str] = {}

    if not isinstance(datos, dict):
        return {
            "datos": "Los datos deben enviarse como un objeto JSON."
        }

    _validar_campos_obligatorios(datos, errores)
    _validar_campos_no_permitidos(
        datos=datos,
        campos_permitidos=CAMPOS_SOLICITUD,
        errores=errores,
    )

    _validar_titulo(datos.get("titulo"), errores)
    _validar_area_solicitante(
        datos.get("area_solicitante"),
        errores,
    )
    _validar_prioridad(datos.get("prioridad"), errores)
    _validar_costo_estimado(
        datos.get("costo_estimado"),
        errores,
    )
    _validar_estado(datos.get("estado"), errores)

    return errores


def validar_actualizacion_estado(
    datos: dict[str, Any],
) -> dict[str, str]:
    """
    Valida una operación PATCH que únicamente permite modificar
    el estado de una solicitud.
    """
    errores: dict[str, str] = {}
    campos_permitidos = {"estado"}

    if not isinstance(datos, dict):
        return {
            "datos": "Los datos deben enviarse como un objeto JSON."
        }

    if "estado" not in datos:
        errores["estado"] = "Este campo es obligatorio."

    _validar_campos_no_permitidos(
        datos=datos,
        campos_permitidos=campos_permitidos,
        errores=errores,
    )

    _validar_estado(datos.get("estado"), errores)

    return errores


def _validar_campos_obligatorios(
    datos: dict[str, Any],
    errores: dict[str, str],
) -> None:
    for campo in CAMPOS_SOLICITUD:
        if campo not in datos:
            errores[campo] = "Este campo es obligatorio."


def _validar_campos_no_permitidos(
    datos: dict[str, Any],
    campos_permitidos: set[str],
    errores: dict[str, str],
) -> None:
    campos_desconocidos = set(datos.keys()) - campos_permitidos

    if campos_desconocidos:
        errores["campos_no_permitidos"] = (
            "Los siguientes campos no están permitidos: "
            + ", ".join(sorted(campos_desconocidos))
            + "."
        )


def _validar_titulo(
    titulo: object,
    errores: dict[str, str],
) -> None:
    if titulo is None:
        return

    if not isinstance(titulo, str):
        errores["titulo"] = "El título debe ser un texto."
        return

    titulo_limpio = titulo.strip()

    if len(titulo_limpio) < 3:
        errores["titulo"] = (
            "El título debe tener al menos 3 caracteres."
        )
        return

    if len(titulo_limpio) > 150:
        errores["titulo"] = (
            "El título no puede superar los 150 caracteres."
        )


def _validar_area_solicitante(
    area_solicitante: object,
    errores: dict[str, str],
) -> None:
    if area_solicitante is None:
        return

    if not isinstance(area_solicitante, str):
        errores["area_solicitante"] = (
            "El área solicitante debe ser un texto."
        )
        return

    area_limpia = area_solicitante.strip()

    if len(area_limpia) < 2:
        errores["area_solicitante"] = (
            "El área solicitante debe tener al menos 2 caracteres."
        )
        return

    if len(area_limpia) > 100:
        errores["area_solicitante"] = (
            "El área solicitante no puede superar los "
            "100 caracteres."
        )


def _validar_prioridad(
    prioridad: object,
    errores: dict[str, str],
) -> None:
    if prioridad is None:
        return

    if isinstance(prioridad, bool) or not isinstance(prioridad, int):
        errores["prioridad"] = (
            "La prioridad debe ser un número entero."
        )
        return

    if not 1 <= prioridad <= 5:
        errores["prioridad"] = (
            "La prioridad debe estar entre 1 y 5."
        )


def _validar_costo_estimado(
    costo_estimado: object,
    errores: dict[str, str],
) -> None:
    if costo_estimado is None:
        return

    if isinstance(costo_estimado, bool):
        errores["costo_estimado"] = (
            "El costo estimado debe ser un número válido."
        )
        return

    try:
        costo_decimal = Decimal(str(costo_estimado))
    except (InvalidOperation, TypeError, ValueError):
        errores["costo_estimado"] = (
            "El costo estimado debe ser un número válido."
        )
        return

    if not costo_decimal.is_finite():
        errores["costo_estimado"] = (
            "El costo estimado debe ser un número finito."
        )
        return

    if costo_decimal < 0:
        errores["costo_estimado"] = (
            "El costo estimado no puede ser negativo."
        )
        return

    if costo_decimal > Decimal("9999999999.99"):
        errores["costo_estimado"] = (
            "El costo estimado supera el valor permitido."
        )
        return

    if abs(costo_decimal.as_tuple().exponent) > 2:
        errores["costo_estimado"] = (
            "El costo estimado puede tener como máximo "
            "2 decimales."
        )


def _validar_estado(
    estado: object,
    errores: dict[str, str],
) -> None:
    if estado is None:
        return

    if not isinstance(estado, str):
        errores["estado"] = "El estado debe ser un texto."
        return

    if estado not in ESTADOS_PERMITIDOS:
        errores["estado"] = (
            "El estado debe ser registrada, en_proceso, "
            "finalizada o cancelada."
        )