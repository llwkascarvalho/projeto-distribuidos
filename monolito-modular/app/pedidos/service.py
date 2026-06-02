from sqlalchemy.orm import Session
from fastapi import HTTPException
from .models import Pedido

def criar_pedido(db: Session, cliente: str, total: float) -> Pedido:
    pedido = Pedido(cliente=cliente, total=total)
    db.add(pedido)
    db.commit()
    db.refresh(pedido)
    return pedido

def listar_pedidos(db: Session) -> list[Pedido]:
    return db.query(Pedido).all()

def cancelar_pedido(db: Session, pedido_id: int) -> Pedido:
    pedido = _get_or_404(db, pedido_id)
    if pedido.status == "pago":
        raise HTTPException(status_code=400, detail="Pedido já pago não pode ser cancelado")
    pedido.status = "cancelado"
    db.commit()
    db.refresh(pedido)
    return pedido

# Contrato cross-módulo (usado por Pagamentos futuramente)
def atualizar_status(db: Session, pedido_id: int, novo_status: str) -> None:
    pedido = _get_or_404(db, pedido_id)
    pedido.status = novo_status

def get_pedido(db: Session, pedido_id: int) -> Pedido:
    return _get_or_404(db, pedido_id)

def _get_or_404(db: Session, pedido_id: int) -> Pedido:
    pedido = db.query(Pedido).filter(Pedido.id == pedido_id).first()
    if not pedido:
        raise HTTPException(status_code=404, detail="Pedido não encontrado")
    return pedido