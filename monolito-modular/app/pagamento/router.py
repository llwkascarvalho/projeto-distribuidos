from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.shared.database import get_db
from .schemas import PagamentoResponse, StatusPagamentoResponse
from . import service

router = APIRouter(prefix="/pagamento", tags=["Pagamento"])

@router.post("/{pedido_id}", response_model=PagamentoResponse)
def processar_pagamento(pedido_id: int, db: Session = Depends(get_db)):
    return service.processar_pagamento(db, pedido_id)

@router.get("/{pedido_id}/status", response_model=StatusPagamentoResponse)
def status_pagamento(pedido_id: int, db: Session = Depends(get_db)):
    return service.consultar_status(db, pedido_id)