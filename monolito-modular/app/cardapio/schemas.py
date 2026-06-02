from pydantic import BaseModel
from typing import Optional

class CardapioItemCreate(BaseModel):
    nome: str
    preco: float
    disponivel: bool = True

class CardapioItemUpdate(BaseModel):
    nome: Optional[str] = None
    preco: Optional[float] = None
    disponivel: Optional[bool] = None

class CardapioItemResponse(BaseModel):
    id: int
    nome: str
    preco: float
    disponivel: bool
    
    model_config = {"from_attributes": True}