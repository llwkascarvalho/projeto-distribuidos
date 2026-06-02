from pydantic import BaseModel


class PagamentoResponse(BaseModel):
    pedido_id: int
    status_pagamento: str
    status_pedido: str
    mensagem: str


class StatusResponse(BaseModel):
    pedido_id: int
    status: str
