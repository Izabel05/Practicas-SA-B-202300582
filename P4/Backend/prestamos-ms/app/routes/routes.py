from fastapi import FastAPI, Request
from strawberry.fastapi import GraphQLRouter

from app.controller.graphql_controller import schema
from app.controller.rest_controller import router as rest_router


async def context_getter(request: Request) -> dict:
    return {"request": request, "loan_service": request.app.state.loan_service}


def register_routes(app: FastAPI) -> None:
    app.include_router(GraphQLRouter(schema, context_getter=context_getter), prefix="/graphql")
    app.include_router(rest_router)
