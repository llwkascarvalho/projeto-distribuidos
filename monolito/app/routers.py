from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from .database import get_db
from .schemas import (
    PedidoCreate, PedidoResponse,
    CardapioItemCreate, CardapioItemUpdate, CardapioItemResponse,
    PagamentoResponse, NotificacaoResponse,
)
from . import services

router = APIRouter()


# Pedidos

@router.post("/pedidos", response_model=PedidoResponse, tags=["Pedidos"])
def criar_pedido(body: PedidoCreate, db: Session = Depends(get_db)):
    """Cria um novo pedido com status 'pendente'."""
    return services.criar_pedido(db, body.cliente, body.total)


@router.get("/pedidos", response_model=list[PedidoResponse], tags=["Pedidos"])
def listar_pedidos(db: Session = Depends(get_db)):
    """Lista todos os pedidos."""
    return services.listar_pedidos(db)


@router.delete("/pedidos/{pedido_id}", tags=["Pedidos"])
def cancelar_pedido(pedido_id: int, db: Session = Depends(get_db)):
    """Cancela um pedido que ainda não foi pago."""
    return services.cancelar_pedido(db, pedido_id)


# Cardápio

@router.post("/cardapio", response_model=CardapioItemResponse, tags=["Cardápio"])
def criar_item(body: CardapioItemCreate, db: Session = Depends(get_db)):
    """Adiciona um item ao cardápio."""
    return services.criar_item_cardapio(db, body.nome, body.preco, body.disponivel)


@router.get("/cardapio", response_model=list[CardapioItemResponse], tags=["Cardápio"])
def listar_cardapio(db: Session = Depends(get_db)):
    """Lista todos os itens do cardápio."""
    return services.listar_cardapio(db)


@router.patch("/cardapio/{item_id}", response_model=CardapioItemResponse, tags=["Cardápio"])
def atualizar_item(item_id: int, body: CardapioItemUpdate, db: Session = Depends(get_db)):
    """Atualiza nome, preço ou disponibilidade de um item."""
    return services.atualizar_item_cardapio(db, item_id, body.model_dump(exclude_none=True))

@router.delete("/cardapio/{item_id}", tags=["Cardápio"])
def deletar_item(item_id: int, db: Session = Depends(get_db)):
    """Remove um item do cardápio."""
    return services.deletar_item_cardapio(db, item_id)


# Pagamento

@router.post("/pagamento/{pedido_id}", tags=["Pagamento"])
def processar_pagamento(pedido_id: int, db: Session = Depends(get_db)):
    """
    Processa o pagamento (mock) de um pedido.
    Regra crítica: só notifica a cozinha após confirmação de pagamento.
    """
    return services.processar_pagamento(db, pedido_id)


@router.get("/pagamento/{pedido_id}/status", tags=["Pagamento"])
def status_pagamento(pedido_id: int, db: Session = Depends(get_db)):
    """Consulta o status do pagamento de um pedido."""
    return services.consultar_status_pagamento(db, pedido_id)


# Notificações

@router.get("/notificacoes", response_model=list[NotificacaoResponse], tags=["Notificações"])
def listar_notificacoes(db: Session = Depends(get_db)):
    """Lista todas as notificações enviadas para a cozinha."""
    return services.listar_notificacoes(db)
