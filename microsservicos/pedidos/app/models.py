from sqlalchemy import Column, Integer, String, Float, DateTime
from sqlalchemy.sql import func
from .database import Base


class Pedido(Base):
    __tablename__ = "pedidos"

    id = Column(Integer, primary_key=True, index=True)
    cliente = Column(String, nullable=False)
    total = Column(Float, nullable=False)
    status = Column(String, default="pendente")  # pendente | pago | cancelado | pagamento_recusado
    criado_em = Column(DateTime(timezone=True), server_default=func.now())
