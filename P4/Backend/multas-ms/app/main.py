from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from psycopg_pool import ConnectionPool

from app.config.settings import Settings
from app.models.errors import ConflictError, InvalidInputError, NotFoundError
from app.repository.postgres_fine_repository import PostgresFineRepository
from app.routes.routes import register_routes
from app.service.fine_service import FineService


def create_app(settings: Settings | None = None, fine_service: FineService | None = None) -> FastAPI:
    selected_settings = settings
    pool: ConnectionPool | None = None

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        nonlocal pool
        if fine_service is None:
            runtime_settings = selected_settings or Settings.from_environment()
            pool = ConnectionPool(runtime_settings.database_url, open=False)
            pool.open()
            pool.wait()
            app.state.fine_service = FineService(
                PostgresFineRepository(pool),
                runtime_settings.daily_rate,
            )
        else:
            app.state.fine_service = fine_service
        yield
        if pool is not None:
            pool.close()

    app = FastAPI(title="API de Multas", version="1.0.0", lifespan=lifespan)
    register_routes(app)

    @app.exception_handler(InvalidInputError)
    async def invalid_input_handler(_: Request, error: InvalidInputError) -> JSONResponse:
        return error_response(status.HTTP_400_BAD_REQUEST, "DATOS_INVALIDOS", str(error))

    @app.exception_handler(NotFoundError)
    async def not_found_handler(_: Request, error: NotFoundError) -> JSONResponse:
        return error_response(status.HTTP_404_NOT_FOUND, "NO_ENCONTRADO", str(error))

    @app.exception_handler(ConflictError)
    async def conflict_handler(_: Request, error: ConflictError) -> JSONResponse:
        return error_response(status.HTTP_409_CONFLICT, "CONFLICTO", str(error))

    return app


def error_response(http_status: int, code: str, message: str) -> JSONResponse:
    return JSONResponse(status_code=http_status, content={"error": {"codigo": code, "mensaje": message}})


app = create_app()
