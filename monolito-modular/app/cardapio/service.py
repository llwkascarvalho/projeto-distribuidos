from sqlalchemy.orm import Session
from fastapi import HTTPException
from .models import CardapioItem

def criar_item(db: Session, nome: str, preco: float, disponivel: bool = True) -> CardapioItem:
    item = CardapioItem(nome=nome, preco=preco, disponivel=disponivel)
    db.add(item)
    db.commit()
    db.refresh(item)
    return item

def listar_itens(db: Session) -> list[CardapioItem]:
    return db.query(CardapioItem).all()

def atualizar_item(db: Session, item_id: int, dados: dict) -> CardapioItem:
    item = _get_or_404(db, item_id)
    for campo, valor in dados.items():
        if valor is not None:
            setattr(item, campo, valor)
    db.commit()
    db.refresh(item)
    return item

def deletar_item(db: Session, item_id: int) -> dict:
    item = _get_or_404(db, item_id)
    db.delete(item)
    db.commit()
    return {"detail": "Item removido"}

def _get_or_404(db: Session, item_id: int) -> CardapioItem:
    item = db.query(CardapioItem).filter(CardapioItem.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item não encontrado")
    return item