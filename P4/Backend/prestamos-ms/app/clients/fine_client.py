import json
from datetime import datetime

import pika

from app.models.errors import ExternalServiceError
from app.models.loan import Loan


class RabbitFineClient:
    def __init__(self, rabbitmq_url: str, queue: str) -> None:
        self._rabbitmq_url = rabbitmq_url
        self._queue = queue

    def create_fine(self, loan: Loan, days_overdue: int) -> None:
        try:
            connection = pika.BlockingConnection(pika.URLParameters(self._rabbitmq_url))
            channel = connection.channel()
            channel.queue_declare(queue=self._queue, durable=True)
            channel.basic_publish(
                exchange="",
                routing_key=self._queue,
                body=json.dumps({
                    "id_prestamo": str(loan.id),
                    "id_usuario": str(loan.user_id),
                    "dias_atraso": days_overdue,
                    "fecha_generacion": datetime.now().astimezone().isoformat(),
                }),
                properties=pika.BasicProperties(delivery_mode=2, content_type="application/json"),
            )
            connection.close()
        except pika.AMQPError as error:
            raise ExternalServiceError("no fue posible publicar el evento de multa") from error
