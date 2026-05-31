from fastapi import FastAPI
from .database import engine, Base
from .routers import router

# Cria todas as tabelas automaticamente na inicialização
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Lanchonete — Monólito",
    description=(
        "Sistema de pedidos de lanchonete — Versão 1 (Monólito).\n\n"
        "Fluxo principal: **POST /cardapio** → **POST /pedidos** → **POST /pagamento/{id}** → cozinha notificada.\n\n"
        "Regra crítica: o pedido só vai para a cozinha após confirmação de pagamento."
    ),
    version="1.0.0",
)

app.include_router(router)


@app.get("/health", tags=["Health"])
def health():
    """Verifica se a aplicação está no ar."""
    return {"status": "ok"}
