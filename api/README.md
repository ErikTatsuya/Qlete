# API

## Deploy no Render

Configure no serviço do Render as variáveis `DATABASE_URL` com a URL do Neon, `ADMIN_USER`, `ADMIN_PASSWORD` e `FRONTEND_ORIGINS` com os domínios Cloudflare Pages separados por vírgula. Não coloque credenciais no repositório.

A API aceita URLs PostgreSQL `postgres://` e `postgresql://` do Neon, usando Psycopg assíncrono e preservando parâmetros como SSL e `channel_binding`. O Render fornece `PORT`; `HOST` usa `0.0.0.0` como padrão. O loop de desenvolvimento automático fica desligado por padrão.

## Execução

```sh
uv sync
uv run main.py
```

## Rotas

- `GET /health`: verifica API e conexão com PostgreSQL.
- `GET /api/quizzes`: lista quizzes sem expor as respostas corretas.
- `POST /api/quizzes`: cria quiz; exige autenticação HTTP Basic.
- `POST /api/quizzes/{quiz_id}/questions/{question_id}/answer`: verifica uma alternativa.

A configuração de CORS e demais middleware fica em `src/core/middleware.py`. Esse é o ponto central para adicionar rate limiting; em produção com mais de uma réplica, use armazenamento compartilhado, como Redis.
