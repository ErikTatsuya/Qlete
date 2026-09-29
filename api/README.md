# API

## Deploy no Render

Configure no serviço do Render as variáveis `DATABASE_URL` com a URL do Neon, `ADMIN_USER`, `ADMIN_PASSWORD`, `ADMIN_SESSION_SECRET`, `APP_ENV=production`, `FRONTEND_ORIGINS` com a origem exata do Cloudflare Pages e `FORWARDED_ALLOW_IPS=*`. Gere `ADMIN_SESSION_SECRET` com um valor aleatório forte, mantenha-o estável entre deploys e não coloque credenciais no repositório. `FORWARDED_ALLOW_IPS=*` só é apropriado quando o serviço só recebe tráfego através do proxy confiável do Render. O cookie `Secure` é ligado automaticamente em produção. O código usa `HOST` (padrão `0.0.0.0`) e `PORT` (padrão `8000`, definido pelo Render) ao iniciar com `uv run main.py`.

A API aceita URLs PostgreSQL `postgres://` e `postgresql://` do Neon, usando Psycopg assíncrono e preservando parâmetros como SSL e `channel_binding`. O Render fornece `PORT`; `HOST` usa `0.0.0.0` como padrão. O loop de desenvolvimento automático fica desligado por padrão.

## Execução

```sh
uv sync
uv run main.py
```

## Rotas

- `GET /health`: verifica API e conexão com PostgreSQL.
- `GET /api/quizzes`: lista quizzes sem expor as respostas corretas.
- `POST /api/quizzes`: cria quiz; exige uma sessão admin válida.
- `GET /api/quizzes/{quiz_id}/admin`: carrega os detalhes de edição, incluindo respostas corretas; exige sessão admin.
- `PUT /api/quizzes/{quiz_id}` e `DELETE /api/quizzes/{quiz_id}`: atualizam e removem quizzes; exigem sessão admin.
- `POST /admin/login`: valida as credenciais e cria um cookie HttpOnly com JWT.
- `GET /admin/me` e `POST /admin/logout`: consultam e encerram a sessão admin.
- `POST /api/quizzes/{quiz_id}/questions/{question_id}/answer`: verifica uma alternativa.

A API aplica limites por IP: 120 requisições por minuto no geral, 5/min no login, 30/min ao responder quizzes, 20/min em operações de escrita e 60/min no health check. O contador fica em memória; com múltiplos workers ou réplicas, use armazenamento compartilhado, como Redis, antes de escalar horizontalmente. Em produção, `APP_ENV=production` desativa as origens locais de desenvolvimento; configure `FRONTEND_ORIGINS` explicitamente.

Antes de produção, aplique migrações de banco versionadas em vez de depender da criação automática de tabelas no startup. Configure o comando de build do frontend como `npm ci && npm run build`, publique `frontend/dist` e defina `VITE_API_URL` com a URL HTTPS pública da API.
