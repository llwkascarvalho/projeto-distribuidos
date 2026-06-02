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


def get_pedido(db: Session, pedido_id: int) -> Pedido:
    pedido = db.query(Pedido).filter(Pedido.id == pedido_id).first()
    if not pedido:
        raise HTTPException(status_code=404, detail="Pedido não encontrado")
    return pedido


def cancelar_pedido(db: Session, pedido_id: int) -> Pedido:
    pedido = get_pedido(db, pedido_id)
    if pedido.status == "pago":
        raise HTTPException(status_code=400, detail="Pedido já pago não pode ser cancelado")
    pedido.status = "cancelado"
    db.commit()
    db.refresh(pedido)
    return pedido


def atualizar_status(db: Session, pedido_id: int, novo_status: str) -> Pedido:
    """
    Endpoint interno chamado pelo serviço de Pagamento via HTTP.
    Não exposto diretamente ao usuário final.
    """
    pedido = get_pedido(db, pedido_id)
    pedido.status = novo_status
    db.commit()
    db.refresh(pedido)
    return pedido
