"""
Resiliência implementada:
  1. Timeout explícito em todas as chamadas HTTP (httpx timeout=5s)
  2. Retry com backoff exponencial na atualização de status do pedido (3 tentativas)
  3. Falha na fila (RabbitMQ off) NÃO derruba o pagamento — fire-and-forget
"""

import os
import time
import logging
import httpx

from sqlalchemy.orm import Session
from fastapi import HTTPException

from .models import Pagamento
from .publisher import publicar_pedido_pago

logger = logging.getLogger(__name__)

PEDIDOS_URL = os.getenv("PEDIDOS_URL", "http://localhost:8001")
HTTP_TIMEOUT = float(os.getenv("HTTP_TIMEOUT", "5"))
MAX_RETRIES = int(os.getenv("MAX_RETRIES", "3"))


# ── Gateway mock ──────────────────────────────────────────────────────────────

def _gateway_mock(pedido_id: int, valor: float) -> bool:
  
    return True


# ── HTTP com retry + timeout

def _get_pedido(pedido_id: int) -> dict:
    try:
        r = httpx.get(
            f"{PEDIDOS_URL}/pedidos/{pedido_id}",
            timeout=HTTP_TIMEOUT,
        )
        if r.status_code == 404:
            raise HTTPException(status_code=404, detail="Pedido não encontrado")
        r.raise_for_status()
        return r.json()
    except httpx.TimeoutException:
        raise HTTPException(status_code=504, detail="Serviço de pedidos não respondeu a tempo")
    except httpx.RequestError as e:
        raise HTTPException(status_code=503, detail=f"Serviço de pedidos indisponível: {e}")


def _atualizar_status_pedido(pedido_id: int, status: str) -> None:
    """
    Atualiza o status do pedido com retry e backoff exponencial.
    """
    for tentativa in range(1, MAX_RETRIES + 1):
        try:
            r = httpx.patch(
                f"{PEDIDOS_URL}/pedidos/{pedido_id}/status",
                json={"status": status},
                timeout=HTTP_TIMEOUT,
            )
            r.raise_for_status()
            logger.info(f"Status do pedido {pedido_id} atualizado para '{status}'")
            return
        except (httpx.TimeoutException, httpx.RequestError) as e:
            wait = 2 ** (tentativa - 1)
            logger.warning(
                f"Tentativa {tentativa}/{MAX_RETRIES} de atualizar status falhou: {e}. "
                f"Aguardando {wait}s..."
            )
            if tentativa < MAX_RETRIES:
                time.sleep(wait)

    raise HTTPException(
        status_code=503,
        detail="Não foi possível atualizar status do pedido após múltiplas tentativas",
    )


# ── Contrato público 

def processar_pagamento(db: Session, pedido_id: int) -> dict:
    # 1. Busca o pedido via HTTP no serviço de Pedidos
    pedido = _get_pedido(pedido_id)

    if pedido["status"] != "pendente":
        raise HTTPException(
            status_code=400,
            detail=f"Pedido está com status '{pedido['status']}', esperado 'pendente'",
        )

    # 2. Registra pagamento no banco próprio
    pagamento = Pagamento(pedido_id=pedido_id, valor=pedido["total"], status="pendente")
    db.add(pagamento)
    db.flush()

    # 3. Processa via gateway mock
    aprovado = _gateway_mock(pedido_id, pedido["total"])
    pagamento.status = "aprovado" if aprovado else "recusado"
    db.commit()

    if aprovado:
        # 4. Atualiza status do pedido via HTTP com retry
        _atualizar_status_pedido(pedido_id, "pago")

        # 5. Publica evento na fila para o serviço de Notificação 
        publicado = publicar_pedido_pago(pedido_id, pedido["total"])

        return {
            "pedido_id": pedido_id,
            "status_pagamento": "aprovado",
            "status_pedido": "pago",
            "mensagem": (
                "Pagamento aprovado. Evento enviado para a fila com sucesso."
                if publicado
                else "Pagamento aprovado. Evento pendente (RabbitMQ indisponível)."
            ),
        }
    else:
        _atualizar_status_pedido(pedido_id, "pagamento_recusado")
        raise HTTPException(status_code=402, detail="Pagamento recusado")


def consultar_status(db: Session, pedido_id: int) -> dict:
    pagamento = (
        db.query(Pagamento)
        .filter(Pagamento.pedido_id == pedido_id)
        .order_by(Pagamento.id.desc())
        .first()
    )
    if not pagamento:
        raise HTTPException(status_code=404, detail="Nenhum pagamento encontrado para este pedido")
    return {"pedido_id": pedido_id, "status": pagamento.status}
