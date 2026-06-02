from fastapi import FastAPI
from .database import engine, Base
from .router import router

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Serviço de Cardápio",
    description="Microsserviço responsável pelo CRUD de itens do cardápio.",
    version="3.0.0",
)

app.include_router(router)


@app.get("/health", tags=["Health"])
def health():
    return {"status": "ok", "servico": "cardapio"}
