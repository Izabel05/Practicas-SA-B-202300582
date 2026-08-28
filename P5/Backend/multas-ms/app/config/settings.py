import os
from dataclasses import dataclass
from decimal import Decimal, InvalidOperation


@dataclass(frozen=True, slots=True)
class Settings:
    database_url: str
    daily_rate: Decimal
    port: int
    rabbitmq_url: str
    fine_queue: str

    @classmethod
    def from_environment(cls) -> "Settings":
        database_url = os.getenv("DATABASE_URL", "")
        if not database_url:
            raise RuntimeError("DATABASE_URL es obligatoria")
        try:
            daily_rate = Decimal(os.getenv("FINE_DAILY_RATE", "5.00"))
        except InvalidOperation as error:
            raise RuntimeError("FINE_DAILY_RATE debe ser decimal") from error
        return cls(
            database_url=database_url,
            daily_rate=daily_rate,
            port=int(os.getenv("PORT", "8084")),
            rabbitmq_url=os.getenv("RABBITMQ_URL", "amqp://guest:guest@rabbitmq:5672/%2F"),
            fine_queue=os.getenv("FINE_QUEUE", "multa.requerida"),
        )
