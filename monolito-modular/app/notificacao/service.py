from sqlalchemy.orm import Session
from .models import Notificacao

def notificar_cozinha(db: Session, pedido_id: int) -> Notificacao:
    mensagem = f"Pedido #{pedido_id} PAGO - preparar agora!"
    notificacao = Notificacao(pedido_id=pedido_id, mensagem=mensagem)
    db.add(notificacao)
    db.flush()
    return notificacao

def listar_notificacoes(db: Session) -> list[Notificacao]:
    return db.query(Notificacao).order_by(Notificacao.id.desc()).all()