# Versão 3 — Microsserviços

Sistema de pedidos de lanchonete implementado como **4 serviços independentes**,
cada um com seu próprio banco, se comunicando via HTTP/REST e RabbitMQ.

## Arquitetura

```
┌──────────────────────────────────────────────────────────────┐
│  Cliente (Swagger / curl)                                    │
└──────┬──────────────────────────┬───────────────────────────-┘
       │                          │
       ▼ :8001                    ▼ :8002
  ┌─────────┐               ┌──────────┐
  │ Pedidos │               │ Cardápio │
  │  (API)  │               │  (API)   │
  └────┬────┘               └──────────┘
       │  HTTP PATCH /pedidos/{id}/status
       │◄──────────────────────┐
       │                       │
       ▼ :8003                 │
  ┌───────────┐  HTTP GET ─────┘
  │ Pagamento │──────────────► Pedidos
  │   (API)   │
  └─────┬─────┘
        │  RabbitMQ (fila: notificacoes)
        ▼
  ┌─────────────┐
  │ Notificação │  :8004
  │  (consumer) │──► persiste notificação no banco próprio
  └─────────────┘
```

## Estrutura de diretórios

```
microsservicos/
├── docker-compose.yml        ← orquestra tudo
├── pedidos/
│   ├── app/{main,database,models,schemas,service,router}.py
│   ├── Dockerfile
│   └── requirements.txt
├── cardapio/
│   ├── app/{main,database,models,schemas,service,router}.py
│   ├── Dockerfile
│   └── requirements.txt
├── pagamento/
│   ├── app/{main,database,models,schemas,service,router,publisher}.py
│   ├── Dockerfile
│   └── requirements.txt
└── notificacao/
    ├── app/{main,database,models,schemas,router,consumer}.py
    ├── Dockerfile
    └── requirements.txt
```

## Como rodar

```bash
cd microsservicos
docker compose up --build
```

Aguarde todos os containers ficarem `healthy` (~30s na primeira vez).

| Serviço | Swagger UI |
|---|---|
| Pedidos | http://localhost:8001/docs |
| Cardápio | http://localhost:8002/docs |
| Pagamento | http://localhost:8003/docs |
| Notificação | http://localhost:8004/docs |
| RabbitMQ UI | http://localhost:15672 (guest/guest) |

## Testando o fluxo completo

### 1. Criar item no cardápio
```
POST http://localhost:8002/cardapio
{"nome": "X-Burguer", "preco": 25.90}
```

### 2. Criar pedido
```
POST http://localhost:8001/pedidos
{"cliente": "João", "total": 25.90}
# Anote o "id" retornado, ex: 1
```

### 3. Processar pagamento
```
POST http://localhost:8003/pagamento/1
```
Internamente:
- Pagamento chama `GET /pedidos/1` no serviço Pedidos (HTTP síncrono)
- Aprova o pagamento
- Chama `PATCH /pedidos/1/status` com `{"status": "pago"}` (HTTP com retry)
- Publica `{"pedido_id": 1, "valor": 25.90}` na fila RabbitMQ (assíncrono)

### 4. Confirmar notificação da cozinha
```
GET http://localhost:8004/notificacoes
```

### 5. Verificar health de cada serviço
```
GET http://localhost:8001/health
GET http://localhost:8002/health
GET http://localhost:8003/health
GET http://localhost:8004/health
```

---

## Experimento obrigatório — Derrubar o serviço de Notificação

### Executar

```bash
# 1. Derrubar APENAS o serviço de notificação
docker compose stop notificacao

# 2. Criar e pagar um pedido normalmente
# POST http://localhost:8001/pedidos  →  {"cliente": "Teste", "total": 10.00}
# POST http://localhost:8003/pagamento/{id}

# 3. Observar a resposta do pagamento
```

### Resultado esperado

O pagamento **é aprovado normalmente**. A resposta será:
```json
{
  "status_pagamento": "aprovado",
  "status_pedido": "pago",
  "mensagem": "Pagamento aprovado. Evento enviado para a fila com sucesso."
}
```

O RabbitMQ **guarda a mensagem na fila** (durable=True, mensagem persistente).

```bash
# 4. Subir o serviço de notificação novamente
docker compose start notificacao

# 5. Verificar as notificações — a mensagem represada será processada automaticamente
GET http://localhost:8004/notificacoes
```

### Conclusão

**O pagamento não falha junto.** A notificação é fire-and-forget: o serviço de
pagamento publica o evento e segue em frente. O serviço de notificação consome
a fila de forma independente, com reconexão automática e backoff exponencial.
Isso é consistência eventual: o pedido fica pago, e a cozinha é notificada
assim que o serviço voltar.

---

## Resiliência implementada

### 1. Timeout explícito (HTTP)
Todas as chamadas HTTP do Pagamento para Pedidos usam `timeout=5s` via `httpx`.
Se o serviço de Pedidos demorar mais de 5s, retorna `504 Gateway Timeout`.

### 2. Retry com backoff exponencial (HTTP)
A atualização de status do pedido tenta até **3 vezes** com espera `1s → 2s → 4s`.
Configurável via variáveis de ambiente `MAX_RETRIES` e `HTTP_TIMEOUT`.

### 3. Fire-and-forget na fila (RabbitMQ)
A publicação na fila **nunca cancela o pagamento**. Falha na fila = aviso no log,
pagamento segue aprovado.

### 4. Reconexão automática no consumer
O consumer RabbitMQ reconecta automaticamente com backoff exponencial (máx 60s)
se a conexão cair, sem precisar reiniciar o container.

---

## Documentação — Rollback apenas do serviço de Pagamento

**Cenário:** deploy com bug foi para produção. Como reverter só o pagamento
sem afetar pedidos, cardápio e notificação?

### Passo a passo

```bash
# 1. Fazer build da versão anterior (imagem tagged)
docker build -t pagamento:v2 ./pagamento

# 2. Parar apenas o serviço de pagamento
docker compose stop pagamento

# 3. Subir com a imagem anterior
docker compose run -d --name pagamento_rollback \
  -p 8003:8003 \
  --env-file pagamento/.env \
  -e PEDIDOS_URL=http://pedidos:8001 \
  -e RABBITMQ_URL=amqp://guest:guest@rabbitmq:5672/ \
  pagamento:v2

# 4. Verificar health
curl http://localhost:8003/health

# 5. Reintegrar ao compose normalmente após validação
docker compose up -d pagamento
```

### Por que é possível sem afetar os outros?

- **Banco isolado:** `pagamento_db` é exclusivo. Rollback não toca `pedidos_db`,
  `cardapio_db` ou `notificacao_db`.
- **Contrato HTTP estável:** enquanto `GET /pedidos/{id}` e
  `PATCH /pedidos/{id}/status` não mudarem de contrato, o pagamento pode ser
  trocado à vontade.
- **Fila durável:** mensagens já publicadas no RabbitMQ não são afetadas.
  O serviço de notificação continua consumindo normalmente durante o rollback.
- **Pedidos e cardápio nem sabem** que o pagamento foi revertido — eles não
  dependem do pagamento, só são chamados por ele.

### Comparação com o Monólito

No monólito v1, "fazer rollback do módulo de pagamento" significa fazer rollback
da **aplicação inteira** — pedidos, cardápio e tudo mais voltam junto,
mesmo que não tenham bugs.
