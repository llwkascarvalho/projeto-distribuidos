from contextlib import asynccontextmanager
from fastapi import FastAPI

from .database import engine, Base
from .router import router
from .consumer import iniciar_consumer_em_background

Base.metadata.create_all(bind=engine)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Inicia o consumer RabbitMQ em background quando a API sobe
    iniciar_consumer_em_background()
    yield



app = FastAPI(
    title="Serviço de Notificação",
    description=(
        "Microsserviço de notificação da cozinha.\n\n"
        "**Modo de operação:** consome a fila `notificacoes` do RabbitMQ de forma assíncrona. "
        "Cada mensagem recebida registra uma notificação no banco próprio.\n\n"
        "**Experimento:** derrube este container e faça um pagamento. "
        "O pagamento será aprovado normalmente. As mensagens ficam na fila do RabbitMQ "
        "e serão processadas quando este serviço voltar."
    ),
    version="3.0.0",
    lifespan=lifespan,
)

app.include_router(router)


@app.get("/health", tags=["Health"])
def health():
    return {"status": "ok", "servico": "notificacao"}
