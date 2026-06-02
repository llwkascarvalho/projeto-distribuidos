from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from .database import get_db
from .schemas import PagamentoResponse, StatusResponse
from . import service

router = APIRouter()


@router.post("/pagamento/{pedido_id}", response_model=PagamentoResponse, tags=["Pagamento"])
def processar_pagamento(pedido_id: int, db: Session = Depends(get_db)):
    """
    Processa pagamento de um pedido (mock).

    Fluxo:
    1. Busca pedido no serviço de Pedidos via HTTP (síncrono, timeout 5s, retry 3x).
    2. Aprova o pagamento via gateway mock.
    3. Publica evento 'pedido_pago' no RabbitMQ (assíncrono, fire-and-forget).
    4. Serviço de Notificação consome a fila e notifica a cozinha independentemente.
    """
    return service.processar_pagamento(db, pedido_id)


@router.get("/pagamento/{pedido_id}/status", response_model=StatusResponse, tags=["Pagamento"])
def status_pagamento(pedido_id: int, db: Session = Depends(get_db)):
    return service.consultar_status(db, pedido_id)
