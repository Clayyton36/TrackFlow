# TrackFlow

Sistema web de rastreamento de entregas. A empresa cadastra entregas e atualiza
o status (com foto de comprovação na coleta e na entrega); o cliente acompanha
tudo por um link público, sem login, com a timeline atualizando via JavaScript
sem recarregar a página.

## Stack

- Django 6 + Django REST Framework
- SQLite em desenvolvimento / PostgreSQL em produção (via `DATABASE_URL`)
- JavaScript puro no front (sem framework) consumindo a API pública
- Pillow para processar fotos de comprovação (remove EXIF/GPS, redimensiona)

## Rodando localmente

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env

python manage.py migrate
python manage.py createsuperuser   # opcional, acesso ao /admin/
python manage.py runserver
```

Acesse:
- `http://localhost:8000/cadastro/` — cria a conta da empresa
- `http://localhost:8000/dashboard/` — painel da empresa (cria entregas, atualiza status)
- `http://localhost:8000/rastreio/<codigo>/` — página pública de rastreio

## Rodando os testes

```bash
python manage.py test entregas
```

Cobrem: geração/unicidade do código de rastreio, máquina de estados de status
(transições válidas/inválidas), obrigatoriedade de foto em COLETADO/ENTREGUE,
e que o endpoint público não vaza dados sensíveis (empresa, contato do cliente).

## Modelo de dados

- **Empresa** — ligada a um `User` do Django (login pronto, senha com hash)
- **Entrega** — código de rastreio único (`TRK-XXXXXX`), origem, destino, transportadora
- **StatusHistorico** — cada mudança de status da entrega, com data/hora, observação
  e foto opcional (obrigatória em `COLETADO` e `ENTREGUE`)

Fluxo de status válido: `AGENDADO → COLETADO → EM_TRANSITO → SAIU_PARA_ENTREGA → ENTREGUE`,
com `EXTRAVIADO` possível a partir de qualquer etapa após a coleta. As transições
são validadas em `entregas/models.py::StatusHistorico.transicao_valida`.

## API REST

`GET /api/rastreio/<codigo>/` — público, sem autenticação. Retorna status atual
e timeline completa (incluindo URL das fotos). Não expõe dados da empresa nem
contato do cliente.

Documentação interativa (Swagger UI) em `/api/docs/`; schema OpenAPI bruto em
`/api/schema/`.

## Integração com ViaCEP

No formulário de nova entrega, os campos de CEP de origem/destino consultam a
[ViaCEP](https://viacep.com.br/) direto do navegador (`static/js/cep.js`) e
preenchem o campo de endereço automaticamente — sem envolver o backend. É
opcional: quem preferir digitar o endereço à mão pode ignorar o CEP.

## Deploy

1. Suba o código num repositório Git/GitHub.
2. Crie um Postgres (ex: Railway) e defina `DATABASE_URL` nas variáveis de ambiente.
3. (Opcional, recomendado em produção) Crie uma conta Cloudinary gratuita e defina
   `CLOUDINARY_URL` — sem isso, as fotos enviadas seriam perdidas a cada deploy,
   já que o disco do Render/Railway é efêmero. Descomente as duas linhas do
   Cloudinary no `requirements.txt` antes de instalar.
4. Defina `SECRET_KEY`, `DEBUG=False` e `ALLOWED_HOSTS` com o domínio do serviço.
5. O `Procfile` já roda `migrate` e `collectstatic` antes de subir o `gunicorn` (Railway não executa a fase `release:` do Procfile como o Heroku, por isso está tudo embutido no comando `web`).

## Acessibilidade

- Link "pular para o conteúdo", labels associados aos campos de formulário,
  foco visível em todos os elementos interativos.
- Timeline de rastreio com `aria-live="polite"` — leitores de tela anunciam
  quando o status muda, mesmo sem reload da página.
- Contraste de cores testado em modo claro e escuro (`prefers-color-scheme`).
- Fotos de comprovação têm texto alternativo (`alt`) descritivo.

## PWA (instalável no celular)

O site é um Progressive Web App: `static/manifest.json` + service worker em
`/sw.js` (servido na raiz via `WHITENOISE_ROOT`, necessário pro escopo do
service worker cobrir o site inteiro). Isso permite "Adicionar à tela inicial"
no Android/iOS. O service worker só faz cache de arquivos estáticos
(CSS/JS/ícones) — páginas e a API de rastreio sempre vão direto pra rede, pra
nunca mostrar um status de entrega desatualizado.

Pra publicar na Google Play Store sem reescrever nada, dá pra empacotar esse
PWA com [PWABuilder](https://www.pwabuilder.com/) ou
[Bubblewrap](https://github.com/GoogleChromeLabs/bubblewrap) (gera um TWA —
Trusted Web Activity). Isso exige uma conta de desenvolvedor Google Play
(paga, única vez) que só você pode criar.
