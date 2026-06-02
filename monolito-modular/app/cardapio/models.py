from sqlalchemy import Column, Integer, String, Float, Boolean
from app.shared.database import Base

class CardapioItem(Base):
    __tablename__ = "itens"
    __table_args__ = {"schema": "cardapio"}
    
    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String, nullable=False)
    preco = Column(Float, nullable=False)
    disponivel = Column(Boolean, default=True)