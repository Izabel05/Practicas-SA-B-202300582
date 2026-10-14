import json
from datetime import datetime

import pika
from opentelemetry import trace
from opentelemetry.propagate import inject
from opentelemetry.trace import SpanKind

from app.models.errors import ExternalServiceError
from app.models.loan import Loan


class RabbitFineClient:
    def __init__(self, rabbitmq_url: str, queue: str) -> None:
        self._rabbitmq_url = rabbitmq_url
        self._queue = queue

    def create_fine(self, loan: Loan, days_overdue: int) -> None:
        trace_headers: dict[str, str] = {}
        inject(trace_headers)
        try:
            with trace.get_tracer(__name__).start_as_current_span(
                "multas.publicar_evento", kind=SpanKind.PRODUCER
            ) as span:
                span.set_attribute("messaging.destination.name", self._queue)
                span.set_attribute("library.loan.id", str(loan.id))
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
                    properties=pika.BasicProperties(
                        delivery_mode=2,
                        content_type="application/json",
                        headers=trace_headers,
                    ),
                )
                connection.close()
        except pika.AMQPError as error:
            raise ExternalServiceError("no fue posible publicar el evento de multa") from error
