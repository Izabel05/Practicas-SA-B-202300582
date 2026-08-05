from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config.settings import Settings
from app.dependencies.auth_dependencie import get_database
from app.exceptions.handlers import register_exception_handlers
from app.routes.auth_routes import router as auth_router


Settings.validate()


@asynccontextmanager
async def lifespan(
    app: FastAPI,
) -> AsyncGenerator[None, None]:
    """Administra el inicio y cierre de la aplicación."""

    database = get_database()
    database.open()

    try:
        yield
    finally:
        database.close()


app = FastAPI(
    title=Settings.APP_NAME,
    version=Settings.APP_VERSION,
    debug=Settings.DEBUG,
    lifespan=lifespan,
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


register_exception_handlers(app)

app.include_router(auth_router)


@app.get(
    "/api/health",
    tags=["Sistema"],
)
def health_check() -> dict[str, str]:
    return {
        "status": "OK",
        "application": Settings.APP_NAME,
        "version": Settings.APP_VERSION,
    }