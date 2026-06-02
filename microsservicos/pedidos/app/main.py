from fastapi import FastAPI
from .database import engine, Base
from .router import router

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Serviço de Pedidos",
    description="Microsserviço responsável por criar, listar e cancelar pedidos.",
    version="3.0.0",
)

app.include_router(router)


@app.get("/health", tags=["Health"])
def health():
    return {"status": "ok", "servico": "pedidos"}
