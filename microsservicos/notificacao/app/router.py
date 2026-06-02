from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from .database import get_db
from .models import Notificacao
from .schemas import NotificacaoResponse

router = APIRouter()


@router.get("/notificacoes", response_model=list[NotificacaoResponse], tags=["Notificações"])
def listar_notificacoes(db: Session = Depends(get_db)):
    return db.query(Notificacao).order_by(Notificacao.id.desc()).all()
