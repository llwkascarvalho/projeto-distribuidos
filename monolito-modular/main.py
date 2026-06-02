from fastapi import FastAPI
from sqlalchemy import text
from app.shared.database import engine, Base

def criar_schemas():
    """Cria os schemas do PostgreSQL antes das tabelas."""
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

@app.get("/health", tags=["Health"])
def health():
    return {"status": "ok", "versao": "monolito-modular"}