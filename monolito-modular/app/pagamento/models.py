from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func
from app.shared.database import Base

class Pagamento(Base):
    __tablename__ = "pagamentos"
    __table_args__ = {"schema": "pagamento"}

    id = Column(Integer, primary_key=True, index=True)
    pedido_id = Column(Integer, nullable=False)
    status = Column(String, default="pendente")
    criado_em = Column(DateTime(timezone=True), server_default=func.now())