from pydantic import BaseModel
from typing import Optional


# Pedido

class PedidoCreate(BaseModel):
    cliente: str
    total: float


class PedidoResponse(BaseModel):
    id: int
    cliente: str
    total: float
    status: str

    model_config = {"from_attributes": True}


# Cardapio

class CardapioItemCreate(BaseModel):
    nome: str
    preco: float
    disponivel: bool = True


class CardapioItemUpdate(BaseModel):
    nome: Optional[str] = None
    preco: Optional[float] = None
    disponivel: Optional[bool] = None


class CardapioItemResponse(BaseModel):
    id: int
    nome: str
    preco: float
    disponivel: bool

    model_config = {"from_attributes": True}


# Pagamento

class PagamentoResponse(BaseModel):
    pedido_id: int
    status_pagamento: str
    status_pedido: str
    notificacao: str


# Notificacao

class NotificacaoResponse(BaseModel):
    id: int
    pedido_id: int
    mensagem: str

    model_config = {"from_attributes": True}
