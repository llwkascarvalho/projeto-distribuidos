from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey, DateTime
from sqlalchemy.sql import func
from .database import Base


class Pedido(Base):
    __tablename__ = "pedidos"

    id = Column(Integer, primary_key=True, index=True)
    cliente = Column(String, nullable=False)
    total = Column(Float, nullable=False)
    status = Column(String, default="pendente")  # pendente | pago | cancelado
    criado_em = Column(DateTime(timezone=True), server_default=func.now())


class CardapioItem(Base):
    __tablename__ = "cardapio"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String, nullable=False)
    preco = Column(Float, nullable=False)
    disponivel = Column(Boolean, default=True)


class Pagamento(Base):
    __tablename__ = "pagamentos"

    id = Column(Integer, primary_key=True, index=True)
    pedido_id = Column(Integer, ForeignKey("pedidos.id"), nullable=False)
    status = Column(String, default="pendente")  # pendente | aprovado | recusado
    criado_em = Column(DateTime(timezone=True), server_default=func.now())


class Notificacao(Base):
    __tablename__ = "notificacoes"

    id = Column(Integer, primary_key=True, index=True)
    pedido_id = Column(Integer, ForeignKey("pedidos.id"), nullable=False)
    mensagem = Column(String)
    enviado_em = Column(DateTime(timezone=True), server_default=func.now())
