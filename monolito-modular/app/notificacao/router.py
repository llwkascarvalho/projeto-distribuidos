from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.shared.database import get_db
from .schemas import NotificacaoResponse
from . import service

router = APIRouter(prefix="/notificacoes", tags=["Notificações"])

@router.get("", response_model=list[NotificacaoResponse])
def listar_notificacoes(db: Session = Depends(get_db)):
    return service.listar_notificacoes(db)