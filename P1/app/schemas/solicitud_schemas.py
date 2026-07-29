#valida los datos de netrada y de salida
from decimal import Decimal, InvalidOperation


ESTADOS_PERMITIDOS = {
    "registrada",
    "en_proceso",
    "finalizada",
    "cancelada"
}


def validar_solicitud(datos: dict, es_actualizacion: bool = False) -> dict:
    errores = {}

    campos_obligatorios = {
        "titulo",
        "area_solicitante",
        "prioridad",
        "costo_estimado",
        "estado",
    }

    if not es_actualizacion:
        for campo in campos_obligatorios:
            if campo not in datos:
                errores[campo] = "Este campo es obligatorio."

    titulo = datos.get("titulo")
    if titulo is not None:
        if not isinstance(titulo, str) or len(titulo.strip()) < 3:
            errores["titulo"] = (
                "El título debe ser un texto de al menos 3 caracteres."
            )

    area = datos.get("area_solicitante")
    if area is not None:
        if not isinstance(area, str) or len(area.strip()) < 2:
            errores["area_solicitante"] = (
                "El área solicitante debe ser un texto válido."
            )

    prioridad = datos.get("prioridad")
    if prioridad is not None:
        if not isinstance(prioridad, int) or not 1 <= prioridad <= 5:
            errores["prioridad"] = (
                "La prioridad debe ser un número entero entre 1 y 5."
            )

    costo = datos.get("costo_estimado")
    if costo is not None:
        try:
            costo_decimal = Decimal(str(costo))

            if costo_decimal < 0:
                errores["costo_estimado"] = (
                    "El costo estimado no puede ser negativo."
                )
        except (InvalidOperation, TypeError):
            errores["costo_estimado"] = (
                "El costo estimado debe ser un número válido."
            )

    estado = datos.get("estado")
    if estado is not None and estado not in ESTADOS_PERMITIDOS:
        errores["estado"] = (
            "El estado debe ser registrada, en_proceso o finalizada."
        )

    return errores