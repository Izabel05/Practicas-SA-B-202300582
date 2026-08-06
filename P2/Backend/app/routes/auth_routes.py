from typing import Annotated
from fastapi import APIRouter, Depends, Request, Response, status
from app.controller.token_controller import TokenController
from app.controller.login_controller import LoginController
from app.controller.registro_controller import RegistroController
from app.dependencies.auth_dependencie import (
    get_login_controller,
    get_registro_controller,
    get_token_controller,
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
@router.post(
    "/refresh",
    status_code=status.HTTP_200_OK,
)
def refresh_token(
    request: Request,
    response: Response,
    controller: Annotated[
        TokenController,
        Depends(get_token_controller),
    ],
) -> dict[str, str]:
    return controller.refresh(
        request=request,
        response=response,
    )

@router.post(
    "/logout",
    status_code=status.HTTP_200_OK,
)
def logout_user(
    response: Response,
    controller: Annotated[
        LoginController,
        Depends(get_login_controller),
    ],
) -> dict[str, str]:
    return controller.logout(response)