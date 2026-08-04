import os

from dotenv import load_dotenv


load_dotenv()


class Settings:
    """Centraliza las configuraciones de la aplicación."""

    DATABASE_URL = os.getenv("DATABASE_URL")
    APP_NAME = os.getenv("APP_NAME", "Login API")
    APP_VERSION = os.getenv("APP_VERSION", "1.0.0")
    DEBUG = os.getenv("DEBUG", "False").lower() == "true"

    @classmethod
    def validate(cls) -> None:
        """Comprueba que las variables obligatorias estén configuradas."""

        if not cls.DATABASE_URL:
            raise RuntimeError(
                "DATABASE_URL no está configurada en el archivo .env."
            )