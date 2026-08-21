import os
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Settings:
    database_url: str
    catalog_url: str
    fines_url: str
    port: int

    @classmethod
    def from_environment(cls) -> "Settings":
        database_url = os.getenv("DATABASE_URL", "")
        if not database_url:
            raise RuntimeError("DATABASE_URL es obligatoria")
        return cls(
            database_url=database_url,
            catalog_url=os.getenv("CATALOG_URL", "http://catalogo-ms:8082"),
            fines_url=os.getenv("FINES_URL", "http://multas-ms:8084"),
            port=int(os.getenv("PORT", "8083")),
        )
