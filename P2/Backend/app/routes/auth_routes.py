from typing import Annotated

from fastapi import APIRouter, Depends, Response, status

from app.controller.login_controller import LoginController
from app.controller.registro_controller import RegistroController
from app.dependencies.auth_dependencie import (
    get_login_controller,
    get_registro_controller,
)
from app.schemas.auth_schema import AuthSchema
from app.schemas.login_schema import LoginSchema
from app.schemas.registro_schema import RegisterSchema


router = APIRouter(
    prefix="/api/auth",
    tags=["Autenticacion"],
)


@router.post(
    "/register",
    response_model=AuthSchema,
    status_code=status.HTTP_201_CREATED,
)
def register_user(
    schema: RegisterSchema,
    controller: Annotated[
        RegistroController,
        Depends(get_registro_controller),
    ],
) -> AuthSchema:
    return controller.register(schema)


@router.post(
    "/login",
    response_model=AuthSchema,
    status_code=status.HTTP_200_OK,
)
def login_user(
    schema: LoginSchema,
    response: Response,
    controller: Annotated[
        LoginController,
        Depends(get_login_controller),
    ],
) -> AuthSchema:
    return controller.login(
        schema=schema,
        response=response,
    )