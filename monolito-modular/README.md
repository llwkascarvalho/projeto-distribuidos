# Versão 2 — Monólito Modular

Sistema de pedidos de lanchonete implementado em uma única aplicação, mas com fronteiras explícitas entre os módulos e schemas separados no banco de dados.

## Estrutura do Banco (Schemas)

Diferente da Versão 1, aqui o banco único possui divisões lógicas.
- `pedidos.pedidos`
- `cardapio.itens`
- `pagamento.pagamentos`
- `notificacao.notificacoes`

## Como rodar

### Opção 1 — Docker Compose (recomendado)

```bash
docker compose up --build
```
A API fica disponível em `http://localhost:8001`.

Swagger UI: `http://localhost:8001/docs`

### Opção 2 — Local (Python)

Pré-requisito: PostgreSQL rodando com as credenciais do .env.

```bash
python -m venv venv
# Windows:
venv\Scripts\activate
# Linux/macOS:
source venv/bin/activate

pip install -r requirements.txt
uvicorn main:app --reload --port 8001
```

### Testando via Swagger

Acesse http://localhost:8001/docs e siga o fluxo:

    POST /cardapio — crie um item.

    POST /pedidos — crie um pedido (status ficará 'pendente').

    POST /pagamento/{id} — processe o pagamento do pedido.

    GET /notificacoes — verifique a notificação gerada para a cozinha.

    GET /health — verifique o status da aplicação.

### Respostas Obrigatórias do Documento
**1. Experimento: Trocar a implementação do módulo de pagamento**

- O objetivo do experimento é provar que a alteração interna de um módulo não afeta os outros.  

- Como fazer:
Abra o arquivo app/pagamento/service.py e altere a função interna _gateway_mock:

```
Python
Mude de True (Aprova sempre):
def _gateway_mock(pedido_id: int) -> bool:
    return True

Para False (Recusa sempre):
def _gateway_mock(pedido_id: int) -> bool:
    return False
``` 

### Esforço documentado:

- Arquivos alterados: Apenas 1 (app/pagamento/service.py).

- Impacto em outros módulos: Zero. Nenhuma linha de código precisou ser alterada em pedidos, cardapio ou notificacoes, provando que o isolamento por interfaces públicas funciona.  

### 2. Documentação: Quais módulos poderiam virar serviços independentes amanhã? O que falta?

Prontos para separação rápida:

    Cardápio: É o mais isolado. Não depende de nenhum outro módulo para funcionar.

    Notificação: Também está isolado no nível de dados.

### O que falta para virarem Microsserviços de fato?   

- Comunicação pela rede: Atualmente os módulos usam importação de código (from app.pedidos import service). Isso precisaria ser trocado por requisições HTTP (ex: biblioteca httpx) ou envio de mensagens para uma fila (Kafka/RabbitMQ).  

- Separação física do banco: O banco atual é único, com schemas separados. Para microsserviços reais, o banco precisa ser fisicamente quebrado, cada um com sua própria string de conexão e gerador de banco (database.py exclusivo).  

- Deploy isolado: Cada módulo precisaria de seu próprio Dockerfile e sua própria porta no docker-compose.yml, subindo como processos totalmente independentes.