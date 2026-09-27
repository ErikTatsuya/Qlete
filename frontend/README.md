# Frontend

## Cloudflare Pages

Configure `VITE_API_URL` nas variáveis de build do projeto Pages com a URL pública do serviço Render. A variável é incluída no bundle durante o build; faça novo deploy após alterá-la. Use `npm run build` como comando de build e `dist` como diretório de saída.

## Desenvolvimento local

Execute `npm install` e `npm run dev`. Se quiser encaminhar chamadas locais para uma API, configure `API_PROXY_TARGET` no ambiente antes de iniciar o Vite; não há destino de API fixo no código.
