from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from .database import get_db
from .schemas import PedidoCreate, PedidoResponse, StatusUpdate
from . import service

router = APIRouter()


@router.post("/pedidos", response_model=PedidoResponse, tags=["Pedidos"])
def criar_pedido(body: PedidoCreate, db: Session = Depends(get_db)):
    """Cria um novo pedido com status 'pendente'."""
    return service.criar_pedido(db, body.cliente, body.total)


@router.get("/pedidos", response_model=list[PedidoResponse], tags=["Pedidos"])
def listar_pedidos(db: Session = Depends(get_db)):
    """Lista todos os pedidos."""
    return service.listar_pedidos(db)


@router.get("/pedidos/{pedido_id}", response_model=PedidoResponse, tags=["Pedidos"])
def get_pedido(pedido_id: int, db: Session = Depends(get_db)):
    """Retorna um pedido pelo ID."""
    return service.get_pedido(db, pedido_id)


@router.delete("/pedidos/{pedido_id}", tags=["Pedidos"])
def cancelar_pedido(pedido_id: int, db: Session = Depends(get_db)):
    """Cancela um pedido que ainda não foi pago."""
    return service.cancelar_pedido(db, pedido_id)


@router.patch("/pedidos/{pedido_id}/status", response_model=PedidoResponse, tags=["Interno"])
def atualizar_status(pedido_id: int, body: StatusUpdate, db: Session = Depends(get_db)):
    """
    Endpoint interno — chamado apenas pelo serviço de Pagamento.
    Atualiza o status do pedido após processamento do pagamento.
    """
    return service.atualizar_status(db, pedido_id, body.status)
