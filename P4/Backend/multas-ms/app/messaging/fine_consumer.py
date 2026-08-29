import json
import logging
import threading
import time
from datetime import datetime
from uuid import UUID

import pika

from app.service.fine_service import FineService

LOGGER = logging.getLogger(__name__)


class FineEventConsumer:
    def __init__(self, rabbitmq_url: str, queue: str, service: FineService) -> None:
        self._rabbitmq_url = rabbitmq_url
        self._queue = queue
        self._service = service
        self._stop = threading.Event()
        self._connection: pika.BlockingConnection | None = None
        self._thread = threading.Thread(target=self._run, daemon=True, name="fine-events")

    def start(self) -> None:
        self._thread.start()

    def close(self) -> None:
        self._stop.set()
        if self._connection and self._connection.is_open:
            self._connection.add_callback_threadsafe(self._connection.stop_ioloop)
        self._thread.join(timeout=10)

    def _run(self) -> None:
        while not self._stop.is_set():
            try:
                self._consume()
            except Exception:
                LOGGER.exception("Conexion con RabbitMQ interrumpida")
                self._stop.wait(5)

    def _consume(self) -> None:
        self._connection = pika.BlockingConnection(pika.URLParameters(self._rabbitmq_url))
        channel = self._connection.channel()
        channel.queue_declare(queue=self._queue, durable=True)
        channel.basic_qos(prefetch_count=1)

        def handle(ch, method, _properties, body) -> None:
            try:
                event = json.loads(body)
                generated_at = event.get("fecha_generacion")
                self._service.create_for_overdue_loan(
                    UUID(event["id_prestamo"]),
                    UUID(event["id_usuario"]),
                    int(event["dias_atraso"]),
                    datetime.fromisoformat(generated_at) if generated_at else None,
                )
                ch.basic_ack(method.delivery_tag)
            except Exception:
                LOGGER.exception("Evento de multa invalido")
                ch.basic_nack(method.delivery_tag, requeue=False)

        channel.basic_consume(queue=self._queue, on_message_callback=handle)
        channel.start_consuming()
