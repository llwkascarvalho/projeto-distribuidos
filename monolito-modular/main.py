from fastapi import FastAPI
from sqlalchemy import text
from app.shared.database import engine, Base
import app.cardapio.models
import app.notificacao.models
import app.pedidos.models
from app.cardapio.router import router as cardapio_router
from app.notificacao.router import router as notificacao_router
from app.pedidos.router import router as pedidos_router

def criar_schemas():
    with engine.connect() as conn:
        for schema in ("pedidos", "cardapio", "pagamento", "notificacao"):
            conn.execute(text(f"CREATE SCHEMA IF NOT EXISTS {schema}"))
        conn.commit()

criar_schemas()
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Lanchonete — Monólito Modular",
    description="Sistema de pedidos de lanchonete — Versão 2 (Monólito Modular).",
    version="2.0.0",
)

app.include_router(cardapio_router)
app.include_router(notificacao_router)
app.include_router(pedidos_router)

@app.get("/health", tags=["Health"])
def health():
    return {"status": "ok", "versao": "monolito-modular"}