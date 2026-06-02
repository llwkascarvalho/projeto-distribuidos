from pydantic import BaseModel


class PedidoCreate(BaseModel):
    cliente: str
    total: float


class PedidoResponse(BaseModel):
    id: int
    cliente: str
    total: float
    status: str

    model_config = {"from_attributes": True}


class StatusUpdate(BaseModel):
    status: str
