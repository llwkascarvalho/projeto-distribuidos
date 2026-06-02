from sqlalchemy import Column, Integer, String, Float, DateTime
from sqlalchemy.sql import func
from app.shared.database import Base

class Pedido(Base):
    __tablename__ = "pedidos"
    __table_args__ = {"schema": "pedidos"}

    id = Column(Integer, primary_key=True, index=True)
    cliente = Column(String, nullable=False)
    total = Column(Float, nullable=False)
    status = Column(String, default="pendente")
    criado_em = Column(DateTime(timezone=True), server_default=func.now())