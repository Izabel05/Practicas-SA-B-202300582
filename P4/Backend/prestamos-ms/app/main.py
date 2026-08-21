from contextlib import asynccontextmanager

from fastapi import FastAPI
from psycopg_pool import ConnectionPool

from app.clients.catalog_client import HttpCatalogClient
from app.clients.fine_client import HttpFineClient
from app.config.settings import Settings
from app.repository.postgres_loan_repository import PostgresLoanRepository
from app.routes.routes import register_routes
from app.service.loan_service import LoanService


def create_app(
    settings: Settings | None = None,
    loan_service: LoanService | None = None,
) -> FastAPI:
    selected_settings = settings
    pool: ConnectionPool | None = None

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        nonlocal pool
        if loan_service is None:
            runtime_settings = selected_settings or Settings.from_environment()
            pool = ConnectionPool(runtime_settings.database_url, open=False)
            pool.open()
            pool.wait()
            app.state.loan_service = LoanService(
                PostgresLoanRepository(pool),
                HttpCatalogClient(runtime_settings.catalog_url),
                HttpFineClient(runtime_settings.fines_url),
            )
        else:
            app.state.loan_service = loan_service
        yield
        if pool is not None:
            pool.close()

    app = FastAPI(title="API de Préstamos", version="1.0.0", lifespan=lifespan)
    register_routes(app)
    return app


app = create_app()
