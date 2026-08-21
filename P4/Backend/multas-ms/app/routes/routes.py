from fastapi import FastAPI

from app.controller.fine_controller import router as fine_router


def register_routes(app: FastAPI) -> None:
    @app.get("/health")
    def health() -> dict[str, str]:
        return {"status": "ok", "servicio": "multas-ms"}

    app.include_router(fine_router)
