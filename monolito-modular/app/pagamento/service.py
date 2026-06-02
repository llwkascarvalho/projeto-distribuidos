from sqlalchemy.orm import Session
from fastapi import HTTPException

# Comunicação cross-módulo via interfaces públicas
from app.pedidos import service as pedido_service
from app.notificacao import service as notificacao_service
from .models import Pagamento

def _gateway_mock(pedido_id: int) -> bool:
    """Implementação mock do gateway de pagamento (sempre aprova)."""
    return True

def processar_pagamento(db: Session, pedido_id: int) -> dict:
    # 1. Lê o pedido via interface do módulo Pedidos
    pedido = pedido_service.get_pedido(db, pedido_id)

    if pedido.status != "pendente":
        raise HTTPException(
            status_code=400,
            detail=f"Pedido está com status '{pedido.status}', esperado 'pendente'",
        )

    # 2. Registra o pagamento no próprio schema
    pagamento = Pagamento(pedido_id=pedido_id, status="pendente")
    db.add(pagamento)
    db.flush()

    # 3. Processa via gateway
    aprovado = _gateway_mock(pedido_id)
    pagamento.status = "aprovado" if aprovado else "recusado"

    # 4. Regra de negócio orquestrada
    if aprovado:
        pedido_service.atualizar_status(db, pedido_id, "pago")
        notificacao = notificacao_service.notificar_cozinha(db, pedido_id)
        
        db.commit()
        return {
            "pedido_id": pedido_id,
            "status_pagamento": "aprovado",
            "status_pedido": "pago",
            "notificacao": notificacao.mensagem,
        }
    else:
        pedido_service.atualizar_status(db, pedido_id, "pagamento_recusado")
        db.commit()
        raise HTTPException(status_code=402, detail="Pagamento recusado")

def consultar_status(db: Session, pedido_id: int) -> dict:
    pagamento = (
        db.query(Pagamento)
        .filter(Pagamento.pedido_id == pedido_id)
        .order_by(Pagamento.id.desc())
        .first()
    )
    if not pagamento:
        raise HTTPException(status_code=404, detail="Nenhum pagamento encontrado para este pedido")
    return {"pedido_id": pedido_id, "status": pagamento.status}