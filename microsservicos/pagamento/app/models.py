from sqlalchemy import Column, Integer, String, Float, DateTime
from sqlalchemy.sql import func
from .database import Base


class Pagamento(Base):
    __tablename__ = "pagamentos"

    id = Column(Integer, primary_key=True, index=True)
    pedido_id = Column(Integer, nullable=False, index=True)
    valor = Column(Float, nullable=False)
    status = Column(String, default="pendente")  
    criado_em = Column(DateTime(timezone=True), server_default=func.now())
