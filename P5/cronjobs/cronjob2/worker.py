import json
import os
import sys
import time
import uuid
from datetime import datetime
from zoneinfo import ZoneInfo

import pika
import psycopg
from psycopg.types.json import Jsonb

DATABASE_URL = os.environ["DATABASE_URL"]
AMQP_URL = os.environ["AMQP_URL"]
QUEUE_NAME = os.getenv("QUEUE_NAME", "resumen.ejecuciones")
TIMEZONE = ZoneInfo("America/Guatemala")


def connect_rabbitmq():
    last_error = None
    for _ in range(30):
        try:
            return pika.BlockingConnection(pika.URLParameters(AMQP_URL))
        except pika.exceptions.AMQPError as error:
            last_error = error
            time.sleep(2)
    raise last_error


def produce_summary():
    with psycopg.connect(DATABASE_URL) as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT to_char(date_trunc('hour', fecha_ejecucion), 'YYYY-MM-DD HH24:00:00'),
                       count(*)
                FROM ejecuciones_cronjob
                GROUP BY date_trunc('hour', fecha_ejecucion)
                ORDER BY date_trunc('hour', fecha_ejecucion)
                """
            )
            executions = [
                {"hora_gmt_6": hour, "cantidad": count}
                for hour, count in cursor.fetchall()
            ]

    message = {
        "evento_id": str(uuid.uuid4()),
        "generado_en_gmt_6": datetime.now(TIMEZONE).replace(tzinfo=None).isoformat(),
        "ejecuciones_por_hora": executions,
    }
    rabbit = connect_rabbitmq()
    try:
        channel = rabbit.channel()
        channel.queue_declare(queue=QUEUE_NAME, durable=True)
        channel.basic_publish(
            exchange="",
            routing_key=QUEUE_NAME,
            body=json.dumps(message).encode(),
            properties=pika.BasicProperties(
                content_type="application/json", delivery_mode=2
            ),
            mandatory=True,
        )
    finally:
        rabbit.close()
    print(json.dumps(message), flush=True)


def prepare_summary_table():
    with psycopg.connect(DATABASE_URL) as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS resumenes_ejecuciones (
                    id BIGSERIAL PRIMARY KEY,
                    evento_id UUID NOT NULL UNIQUE,
                    generado_en TIMESTAMP WITHOUT TIME ZONE NOT NULL,
                    resumen JSONB NOT NULL,
                    recibido_en TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
                )
                """
            )


def consume_summaries():
    prepare_summary_table()
    rabbit = connect_rabbitmq()
    channel = rabbit.channel()
    channel.queue_declare(queue=QUEUE_NAME, durable=True)
    channel.basic_qos(prefetch_count=1)
    open("/tmp/consumer-ready", "w", encoding="utf-8").close()

    def process_message(channel, method, _properties, body):
        try:
            message = json.loads(body)
            with psycopg.connect(DATABASE_URL) as connection:
                with connection.cursor() as cursor:
                    cursor.execute(
                        """
                        INSERT INTO resumenes_ejecuciones
                            (evento_id, generado_en, resumen)
                        VALUES (%s, %s, %s)
                        ON CONFLICT (evento_id) DO NOTHING
                        """,
                        (
                            message["evento_id"],
                            message["generado_en_gmt_6"],
                            Jsonb(message["ejecuciones_por_hora"]),
                        ),
                    )
            channel.basic_ack(delivery_tag=method.delivery_tag)
            print(f"Resumen almacenado: {message['evento_id']}", flush=True)
        except Exception as error:
            print(f"Error procesando resumen: {error}", file=sys.stderr, flush=True)
            channel.basic_nack(delivery_tag=method.delivery_tag, requeue=True)

    channel.basic_consume(queue=QUEUE_NAME, on_message_callback=process_message)
    channel.start_consuming()


if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else ""
    if mode == "producer":
        produce_summary()
    elif mode == "consumer":
        consume_summaries()
    else:
        raise SystemExit("Uso: worker.py producer|consumer")
