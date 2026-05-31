import time
from sqlalchemy.orm import Session
from .models import Pedido, Pagamento, Notificacao
from fastapi import HTTPException


# Pedidos

def criar_pedido(db: Session, cliente: str, total: float) -> Pedido:
    pedido = Pedido(cliente=cliente, total=total)
    db.add(pedido)
    db.commit()
    db.refresh(pedido)
    return pedido


def listar_pedidos(db: Session) -> list[Pedido]:
    return db.query(Pedido).all()


def cancelar_pedido(db: Session, pedido_id: int) -> Pedido:
    pedido = db.query(Pedido).filter(Pedido.id == pedido_id).first()
    if not pedido:
        raise HTTPException(status_code=404, detail="Pedido não encontrado")
    if pedido.status == "pago":
        raise HTTPException(status_code=400, detail="Pedido já pago não pode ser cancelado")
    pedido.status = "cancelado"
    db.commit()
    db.refresh(pedido)
    return pedido


# Cardápio

def criar_item_cardapio(db: Session, nome: str, preco: float, disponivel: bool = True):
    from .models import CardapioItem
    item = CardapioItem(nome=nome, preco=preco, disponivel=disponivel)
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


def listar_cardapio(db: Session):
    from .models import CardapioItem
    return db.query(CardapioItem).all()


def atualizar_item_cardapio(db: Session, item_id: int, dados: dict):
    from .models import CardapioItem
    item = db.query(CardapioItem).filter(CardapioItem.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item não encontrado")
    for campo, valor in dados.items():
        if valor is not None:
            setattr(item, campo, valor)
    db.commit()
    db.refresh(item)
    return item


def deletar_item_cardapio(db: Session, item_id: int):
    from .models import CardapioItem
    item = db.query(CardapioItem).filter(CardapioItem.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item não encontrado")
    db.delete(item)
    db.commit()
    return {"detail": "Item removido"}


# Pagamento

def _simular_pagamento_mock(pedido_id: int) -> bool:
    
    time.sleep(5)
    return True


def processar_pagamento(db: Session, pedido_id: int) -> dict:
    pedido = db.query(Pedido).filter(Pedido.id == pedido_id).first()
    if not pedido:
        raise HTTPException(status_code=404, detail="Pedido não encontrado")
    if pedido.status != "pendente":
        raise HTTPException(
            status_code=400,
            detail=f"Pedido está com status '{pedido.status}', esperado 'pendente'"
        )

    # 1. Registra pagamento
    pagamento = Pagamento(pedido_id=pedido_id, status="pendente")
    db.add(pagamento)
    db.flush()

    # 2. Processa (mock)
    aprovado = _simular_pagamento_mock(pedido_id)
    pagamento.status = "aprovado" if aprovado else "recusado"

    # 3. Regra de negócio: só vai para cozinha se pago
    if aprovado:
        pedido.status = "pago"
        notificacao = notificar_cozinha(db, pedido_id)
        db.commit()
        return {
            "pedido_id": pedido_id,
            "status_pagamento": "aprovado",
            "status_pedido": pedido.status,
            "notificacao": notificacao.mensagem,
        }
    else:
        pedido.status = "pagamento_recusado"
        db.commit()
        raise HTTPException(status_code=402, detail="Pagamento recusado")


def consultar_status_pagamento(db: Session, pedido_id: int) -> dict:
    pagamento = (
        db.query(Pagamento)
        .filter(Pagamento.pedido_id == pedido_id)
        .order_by(Pagamento.id.desc())
        .first()
    )
    if not pagamento:
        raise HTTPException(status_code=404, detail="Nenhum pagamento encontrado para este pedido")
    return {"pedido_id": pedido_id, "status": pagamento.status}


# Notificação

def notificar_cozinha(db: Session, pedido_id: int) -> Notificacao:
    """
    Notifica a cozinha registrando no banco.
    Em produção poderia publicar em uma fila (RabbitMQ/Kafka).
    """
    mensagem = f"Pedido #{pedido_id} PAGO — preparar agora!"
    notificacao = Notificacao(pedido_id=pedido_id, mensagem=mensagem)
    db.add(notificacao)
    # Não faz commit aqui — o commit é feito pelo chamador (processar_pagamento)
    db.flush()
    return notificacao


def listar_notificacoes(db: Session) -> list[Notificacao]:
    return db.query(Notificacao).order_by(Notificacao.id.desc()).all()
