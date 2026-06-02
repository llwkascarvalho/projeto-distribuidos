import os
import json
import logging
import pika

logger = logging.getLogger(__name__)

RABBITMQ_URL = os.getenv("RABBITMQ_URL", "amqp://guest:guest@localhost:5672/")
QUEUE_NAME = "notificacoes"


def publicar_pedido_pago(pedido_id: int, valor: float) -> bool:
    
    try:
        params = pika.URLParameters(RABBITMQ_URL)
        params.socket_timeout = 3  

        connection = pika.BlockingConnection(params)
        channel = connection.channel()

        channel.queue_declare(queue=QUEUE_NAME, durable=True)

        mensagem = json.dumps({"pedido_id": pedido_id, "valor": valor})

        channel.basic_publish(
            exchange="",
            routing_key=QUEUE_NAME,
            body=mensagem,
            properties=pika.BasicProperties(delivery_mode=2),  
        )
        connection.close()
        logger.info(f"Evento publicado na fila: pedido_id={pedido_id}")
        return True

    except Exception as e:
        logger.error(f"Falha ao publicar na fila (pedido continuará pago): {e}")
        return False
