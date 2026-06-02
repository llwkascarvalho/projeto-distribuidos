from pydantic import BaseModel

class PagamentoResponse(BaseModel):
    pedido_id: int
    status_pagamento: str
    status_pedido: str
    notificacao: str

class StatusPagamentoResponse(BaseModel):
    pedido_id: int
    status: str