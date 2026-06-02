from pydantic import BaseModel

class NotificacaoResponse(BaseModel):
    id: int
    pedido_id: int
    mensagem: str
    
    model_config = {"from_attributes": True}