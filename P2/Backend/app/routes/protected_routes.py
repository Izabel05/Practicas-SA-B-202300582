from typing import Annotated

from fastapi import APIRouter, Depends, status

from app.dependencies.auth_dependencie import require_roles
from app.models.role import RoleName


router = APIRouter(
    prefix="/api/protected",
    tags=["Rutas protegidas"],
)


@router.get(
    "/ruta-1",
    status_code=status.HTTP_200_OK,
)
def ruta_admin(
    current_user: Annotated[
        dict,
        Depends(
            require_roles({
                RoleName.ADMIN,
            })
        ),
    ],
) -> dict:
    """Ruta disponible únicamente para administradores."""

    return {
        "message": "Acceso permitido a Ruta 1.",
        "role": current_user["role"],
        "user_id": current_user["sub"],
    }


@router.get(
    "/ruta-2",
    status_code=status.HTTP_200_OK,
)
def ruta_admin_cliente(
    current_user: Annotated[
        dict,
        Depends(
            require_roles({
                RoleName.ADMIN,
                RoleName.CLIENTE,
            })
        ),
    ],
) -> dict:
    """Ruta disponible para administradores y clientes."""

    return {
        "message": "Acceso permitido a Ruta 2.",
        "role": current_user["role"],
        "user_id": current_user["sub"],
    }