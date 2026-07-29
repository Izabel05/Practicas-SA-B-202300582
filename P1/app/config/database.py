from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker

from app.config.settings import Settings

# Verifica que exista DATABASE_URL
Settings.validate()

# Motor de conexión
engine = create_engine(
    Settings.DATABASE_URL,
    pool_pre_ping=True,
    echo=False
)

# Sesiones de trabajo
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# Clase base para todos los modelos
Base = declarative_base()