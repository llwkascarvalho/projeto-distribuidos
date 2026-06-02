import json
import logging
import time
import threading
import os

import pika

from .database import SessionLocal
from .models import Notificacao

logger = logging.getLogger(__name__)

RABBITMQ_URL = os.getenv("RABBITMQ_URL", "amqp://guest:guest@localhost:5672/")
QUEUE_NAME = "notificacoes"


def _processar_mensagem(ch, method, properties, body):
    """Callback executado para cada mensagem recebida da fila."""
    try:
        dados = json.loads(body)
        pedido_id = dados["pedido_id"]
        valor = dados.get("valor", 0)

        mensagem = f"Pedido #{pedido_id} PAGO (R$ {valor:.2f}) — preparar agora!"

        db = SessionLocal()
        try:
            notificacao = Notificacao(pedido_id=pedido_id, mensagem=mensagem)
            db.add(notificacao)
            db.commit()
            logger.info(f"Cozinha notificada: {mensagem}")
        finally:
            db.close()

        # Confirma processamento (ack) — remove da fila
        ch.basic_ack(delivery_tag=method.delivery_tag)

    except Exception as e:
        logger.error(f"Erro ao processar mensagem: {e}")
        # Nack: devolve à fila para reprocessamento
        ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)


def _iniciar_consumer():
    """Loop de reconexão com backoff exponencial."""
    tentativa = 0
    while True:
        try:
            params = pika.URLParameters(RABBITMQ_URL)
            connection = pika.BlockingConnection(params)
            channel = connection.channel()

            channel.queue_declare(queue=QUEUE_NAME, durable=True)
            channel.basic_qos(prefetch_count=1)
            channel.basic_consume(queue=QUEUE_NAME, on_message_callback=_processar_mensagem)

            tentativa = 0  
            logger.info("Consumer conectado ao RabbitMQ. Aguardando mensagens...")
            channel.start_consuming()

        except pika.exceptions.AMQPConnectionError as e:
            tentativa += 1
            wait = min(2 ** tentativa, 60)
            logger.warning(f"RabbitMQ indisponível ({e}). Reconectando em {wait}s...")
            time.sleep(wait)

        except Exception as e:
            logger.error(f"Erro inesperado no consumer: {e}. Reiniciando em 5s...")
            time.sleep(5)


def iniciar_consumer_em_background():
    """Inicia o consumer em uma thread daemon para não bloquear o FastAPI."""
    t = threading.Thread(target=_iniciar_consumer, daemon=True, name="rabbitmq-consumer")
    t.start()
    logger.info("Thread do consumer RabbitMQ iniciada.")
