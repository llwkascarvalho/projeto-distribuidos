from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from .database import get_db
from .schemas import CardapioItemCreate, CardapioItemUpdate, CardapioItemResponse
from . import service

router = APIRouter()


@router.post("/cardapio", response_model=CardapioItemResponse, tags=["Cardápio"])
def criar_item(body: CardapioItemCreate, db: Session = Depends(get_db)):
    return service.criar_item(db, body.nome, body.preco, body.disponivel)


@router.get("/cardapio", response_model=list[CardapioItemResponse], tags=["Cardápio"])
def listar_itens(db: Session = Depends(get_db)):
    return service.listar_itens(db)


@router.patch("/cardapio/{item_id}", response_model=CardapioItemResponse, tags=["Cardápio"])
def atualizar_item(item_id: int, body: CardapioItemUpdate, db: Session = Depends(get_db)):
    return service.atualizar_item(db, item_id, body.model_dump(exclude_none=True))


@router.delete("/cardapio/{item_id}", tags=["Cardápio"])
def deletar_item(item_id: int, db: Session = Depends(get_db)):
    return service.deletar_item(db, item_id)
