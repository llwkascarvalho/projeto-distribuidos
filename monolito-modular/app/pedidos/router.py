from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.shared.database import get_db
from .schemas import PedidoCreate, PedidoResponse
from . import service

router = APIRouter(prefix="/pedidos", tags=["Pedidos"])

@router.post("", response_model=PedidoResponse)
def criar_pedido(body: PedidoCreate, db: Session = Depends(get_db)):
    return service.criar_pedido(db, body.cliente, body.total)

@router.get("", response_model=list[PedidoResponse])
def listar_pedidos(db: Session = Depends(get_db)):
    return service.listar_pedidos(db)

@router.delete("/{pedido_id}")
def cancelar_pedido(pedido_id: int, db: Session = Depends(get_db)):
    return service.cancelar_pedido(db, pedido_id)