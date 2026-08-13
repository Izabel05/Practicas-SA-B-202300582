import os

from dotenv import load_dotenv


load_dotenv()


class Settings:
    """Centraliza las configuraciones de la aplicación."""

    DATABASE_URL = os.getenv("DATABASE_URL")

    APP_NAME = os.getenv("APP_NAME", "Login API")
    APP_VERSION = os.getenv("APP_VERSION", "1.0.0")
    DEBUG = os.getenv("DEBUG", "False").lower() == "true"

    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
    JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")

    JWT_EXPIRATION_SECONDS = int(
        os.getenv("JWT_EXPIRATION_SECONDS", "60")
    )

    JWT_RENEWAL_WINDOW_SECONDS = int(
        os.getenv("JWT_RENEWAL_WINDOW_SECONDS", "60")
    )

    JWT_ISSUER = os.getenv("JWT_ISSUER", "login-api")
    JWT_AUDIENCE = os.getenv("JWT_AUDIENCE", "login-client")

    DATA_ENCRYPTION_KEY = os.getenv("DATA_ENCRYPTION_KEY")
    DATA_SEARCH_KEY = os.getenv("DATA_SEARCH_KEY")

    COOKIE_NAME = os.getenv("COOKIE_NAME", "access_token")
    COOKIE_SECURE = os.getenv(
        "COOKIE_SECURE",
        "False",
    ).lower() == "true"

    COOKIE_SAMESITE = os.getenv(
        "COOKIE_SAMESITE",
        "lax",
    ).lower()

    COOKIE_PATH = os.getenv("COOKIE_PATH", "/")

    DATABASE_POOL_MIN_SIZE = int(
        os.getenv("DATABASE_POOL_MIN_SIZE", "1")
    )

    DATABASE_POOL_MAX_SIZE = int(
        os.getenv("DATABASE_POOL_MAX_SIZE", "5")
    )

    @classmethod
    def validate(cls) -> None:
        """Comprueba que las variables obligatorias estén configuradas."""

        missing_variables: list[str] = []

        if not cls.DATABASE_URL:
            missing_variables.append("DATABASE_URL")

        if not cls.JWT_SECRET_KEY:
            missing_variables.append("JWT_SECRET_KEY")

        if not cls.DATA_ENCRYPTION_KEY:
            missing_variables.append("DATA_ENCRYPTION_KEY")

        if not cls.DATA_SEARCH_KEY:
            missing_variables.append("DATA_SEARCH_KEY")

        if missing_variables:
            names = ", ".join(missing_variables)

            raise RuntimeError(
                "Faltan variables obligatorias en el archivo .env: "
                f"{names}."
            )

        if cls.JWT_EXPIRATION_SECONDS <= 0:
            raise RuntimeError(
                "JWT_EXPIRATION_SECONDS debe ser mayor que cero."
            )

        if cls.JWT_RENEWAL_WINDOW_SECONDS <= 0:
            raise RuntimeError(
                "JWT_RENEWAL_WINDOW_SECONDS debe ser mayor que cero."
            )

        if cls.DATABASE_POOL_MIN_SIZE <= 0:
            raise RuntimeError(
                "DATABASE_POOL_MIN_SIZE debe ser mayor que cero."
            )

        if (
            cls.DATABASE_POOL_MAX_SIZE
            < cls.DATABASE_POOL_MIN_SIZE
        ):
            raise RuntimeError(
                "DATABASE_POOL_MAX_SIZE no puede ser menor que "
                "DATABASE_POOL_MIN_SIZE."
            )

        valid_same_site_values = {"lax", "strict", "none"}

        if cls.COOKIE_SAMESITE not in valid_same_site_values:
            raise RuntimeError(
                "COOKIE_SAMESITE debe ser lax, strict o none."
            )

        if cls.COOKIE_SAMESITE == "none" and not cls.COOKIE_SECURE:
            raise RuntimeError(
                "COOKIE_SECURE debe ser True cuando "
                "COOKIE_SAMESITE es none."
            )
