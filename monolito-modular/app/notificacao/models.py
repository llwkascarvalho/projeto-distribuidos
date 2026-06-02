from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func
from app.shared.database import Base

class Notificacao(Base):
    __tablename__ = "notificacoes"
    __table_args__ = {"schema": "notificacao"}
    
    id = Column(Integer, primary_key=True, index=True)
    pedido_id = Column(Integer, nullable=False)
    mensagem = Column(String, nullable=False)
    enviado_em = Column(DateTime(timezone=True), server_default=func.now())