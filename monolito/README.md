# Versão 1 — Monólito

Sistema de pedidos de lanchonete implementado como uma única aplicação FastAPI + PostgreSQL.

## Estrutura

```
monolito/
├── app/
│   ├── __init__.py
│   ├── main.py        # Ponto de entrada, cria tabelas, registra router
│   ├── database.py    # Conexão com o banco via SQLAlchemy
│   ├── models.py      # Tabelas: pedidos, cardapio, pagamentos, notificacoes
│   ├── schemas.py     # Schemas Pydantic (validação + Swagger)
│   ├── routers.py     # Endpoints HTTP
│   └── services.py    # Lógica de negócio
├── .env
├── docker-compose.yml
├── Dockerfile
└── requirements.txt
```

## Como rodar

### Opção 1 — Docker Compose (recomendado)

```bash
docker compose up --build
```

A API fica disponível em `http://localhost:8000`.  
Swagger UI: `http://localhost:8000/docs`

### Opção 2 — Local (Python)

**Pré-requisito:** PostgreSQL rodando em `127.0.0.1:5433` com as credenciais do `.env`.
*Dica: Você pode subir apenas o banco de dados usando o comando `docker compose up -d db`.*

```bash
cd monolito
python -m venv venv
# Windows:
venv\Scripts\activate
# Linux/macOS:
source venv/bin/activate

pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

## Testando via Swagger

Acesse `http://localhost:8000/docs` e siga o fluxo:

1. **POST /cardapio** — crie um item (ex.: `{"nome": "X-Burguer", "preco": 25.90}`)
2. **POST /pedidos** — crie um pedido (ex.: `{"cliente": "João", "total": 25.90}`)
3. **POST /pagamento/{id}** — processe o pagamento do pedido criado
4. **GET /notificacoes** — verifique que a cozinha foi notificada
5. **GET /health** — verifique o status da aplicação

## Fluxo principal

```
POST /pedidos  →  POST /pagamento/{id}  →  cozinha notificada
     (status: pendente)    (mock aprovado)      (registrado em /notificacoes)
```

**Regra crítica:** o pedido só vai para a cozinha após confirmação de pagamento.  
Se o status do pedido não for `pendente`, o pagamento é rejeitado com 400.

## Experimento obrigatório — Lentidão no pagamento

Em `app/services.py`, na função `_simular_pagamento_mock`:

```python
# time.sleep(5)
```

**O que acontece?**  
Com Uvicorn no modo padrão (assíncrono + thread pool limitado), uma requisição síncrona
bloqueante com `time.sleep(5)` ocupa uma worker thread. Se você disparar várias
requisições simultâneas para `/pagamento`, as demais requisições (inclusive `/pedidos` e
`/cardapio`) vão ficando na fila aguardando uma thread livre.  
Para observar: abra dois terminais e faça `POST /pagamento/1` em um e `GET /pedidos`
em outro ao mesmo tempo — o segundo vai esperar o primeiro terminar.

## Documentação — Escalar o cardápio 10x

**O que precisaria mudar se o módulo de cardápio precisasse escalar 10x?**

No monólito, escalar o cardápio separadamente é **impossível sem reescrever**:

- O banco é único: não dá para isolar réplicas só para a tabela `cardapio` sem
  migrar para uma arquitetura diferente.
- O processo é único: escalar horizontalmente sobe a aplicação inteira (pedidos,
  pagamentos e notificações junto), desperdiçando recursos.
- A solução seria extrair o cardápio para um serviço independente (microsserviço) com
  seu próprio banco e fazer cache com Redis.
