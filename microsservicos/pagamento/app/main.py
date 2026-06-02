from fastapi import FastAPI
from .database import engine, Base
from .router import router

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Serviço de Pagamento",
    description=(
        "Microsserviço de pagamento.\n\n"
        "**Comunicação:** HTTP síncrono com Pedidos | RabbitMQ assíncrono com Notificação.\n\n"
        "**Resiliência:** timeout explícito (5s) + retry com backoff (3x) no HTTP. "
        "Falha na fila não cancela o pagamento."
    ),
    version="3.0.0",
)

app.include_router(router)


@app.get("/health", tags=["Health"])
def health():
    return {"status": "ok", "servico": "pagamento"}
