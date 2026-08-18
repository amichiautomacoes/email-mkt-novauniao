# Email Marketing Pipeline

Pipeline para sincronizar contatos no Supabase, renderizar templates HTML e disparar emails via Resend com controle de limites.

## Estrutura

```text
templates/agosto-2026/catalog.json  catalogo de templates do mes
templates/agosto-2026/raw/          HTMLs originais
templates/agosto-2026/clean/        HTMLs tratados e prontos para envio
src/email_mkt/       codigo da pipeline
scripts/             utilitarios locais
sql/                 migracoes e tabelas Supabase
tests/               testes automatizados
```

## Setup local

```powershell
.\.venv\Scripts\Activate.ps1
pip install -r requirements-dev.txt
$env:PYTHONPATH="src"
```

## Primeiro comando

```powershell
python -m email_mkt.cli send --campaign 3formas-melhorar-experiencia --lote lote2 --limit 10 --dry-run
```

Por padrao, a pipeline nasce em modo seguro. O envio real so deve ser habilitado depois de validar contatos, templates, opt-out e limites do Resend.

## Campanhas e lotes

As campanhas disponiveis sao criadas no catalogo de templates do projeto. Os
lotes sao apenas segmentos na coluna `lote` da tabela
`mkt_novauniao.email_mkt_leads`; eles nao apontam para campanhas no codigo.

```text
campanha disponivel:
3formas-melhorar-experiencia
```

No envio automatico, a planilha define qual campanha sera usada em cada lote.
No envio manual, informe a campanha e o lote explicitamente.

Exemplo:

```powershell
python -m email_mkt.cli send --campaign 3formas-melhorar-experiencia --lote lote1 --limit 50 --dry-run
```

## Limites de envio

A configuracao inicial recomendada para disparos controlados e:

```env
EMAIL_BATCH_SIZE=50
RESEND_REQUESTS_PER_SECOND=1
DRY_RUN_DEFAULT=true
```

Com isso, a pipeline seleciona no maximo a quantidade definida em `--limit`, agrupa ate 50 emails por chamada para a Resend e faz no maximo 1 request por segundo. Enquanto `DRY_RUN_DEFAULT=true`, nenhum email real e enviado.

Para habilitar envio real, defina:

```env
DRY_RUN_DEFAULT=false
```

Ou execute uma campanha explicitamente com:

```powershell
python -m email_mkt.cli send --campaign 3formas-melhorar-experiencia --lote lote1 --limit 50 --no-dry-run
```

## Controle de envio

Os envios reais aceitos pela Resend sao registrados em `mkt_novauniao.email_mkt_envio`:

```text
email          chave primaria
data_envio     ultima data de envio
campanha       ultima campanha/lote enviado
numero_envios  contador acumulado de envios aceitos
```

Execucoes em `--dry-run` nao gravam nessa tabela.

O historico auditavel por etapa fica em `mkt_novauniao.email_mkt_envio_historico`,
criado pela migracao:

```sql
sql/004_email_envio_historico.sql
```

Essa tabela grava uma linha por envio aceito, com `lote_key`, `etapa`,
`template_key`, `resend_email_id` e `data_envio`. Ela tambem impede duplicidade
por email/template e por email/lote/etapa.

Antes de liberar uma etapa nova, confira o status do lote:

```powershell
python -m email_mkt.cli status lote1 --etapa 2
```

A etapa 2 so e executada quando todos os leads ativos do lote tiverem etapa 1
registrada no historico. Exemplo de segundo envio:

```powershell
python -m email_mkt.cli send --campaign 3formas-melhorar-experiencia --lote lote1 --etapa 2 --limit 80 --dry-run
```

## Metricas da Resend

Para sincronizar as metricas da Resend para o Supabase, aplique a migracao:

```sql
sql/003_resend_metrics.sql
```

Ela cria esta estrutura em `mkt_novauniao`:

```text
email_mkt_metricas  snapshots agregados de /emails/metrics
```

Depois execute:

```powershell
$env:PYTHONPATH="src"
python scripts/sync_resend_metrics.py --start-date 2026-08-12
```

O endpoint `GET /emails/metrics` da Resend esta em beta privada. Se a conta
ainda nao tiver acesso, o script avisa o status retornado e nao grava snapshot.

### Webhook da Resend

Para capturar eventos reais de abertura, clique e bounce, rode o
servico de webhook e cadastre esta URL na Resend:

```text
https://emailmkt.targetdados.com/webhooks/resend
```

Eventos recomendados:

```text
email.bounced
email.clicked
email.complained
email.opened
```

Depois de criar o webhook no painel da Resend, copie o signing secret e configure:

```env
RESEND_WEBHOOK_SECRET=whsec_xxxxxxxxxx
```

No EasyPanel, crie um App Service para o receptor:

```text
Service: email-mkt-webhook
Source: GitHub
Builder: Dockerfile
Command: /app/scripts/docker/webhook.sh
Domain: emailmkt.targetdados.com
Port: 8001
```

O endpoint de saude do servico e:

```text
https://emailmkt.targetdados.com/health
```

Os eventos recebidos sao validados com os headers `svix-id`, `svix-timestamp` e
`svix-signature`, e salvos em `mkt_novauniao.email_mkt_metricas`. O `svix-id`
tem indice unico para ignorar reentregas duplicadas da Resend.

## Programacao automatica

O agendamento automatico usa a planilha Google Sheets `Cronograma Email MKT`
como fonte de verdade. A service account precisa ter acesso a essa planilha.

A primeira aba da planilha deve ter estas colunas:

```text
lote | data envio | hora envio | campanha | numero de envios | etapa
```

O script tambem aceita os cabecalhos atuais da planilha:

```text
Leads segmentados | Data do Envio | Horario | Campanha | Numeros envios
```

Cada linha define qual lote de contatos sera buscado no Supabase, qual template
sera usado como campanha e quantos contatos devem ser selecionados. Exemplo:

```text
Lote 1 | 12 ago. | 09:30 | 3formas-melhorar-experiencia | 80
Lote 2 | 13 ago. | 09:30 | campanha 3formas-melhorar-experiencia | 80
```

O prefixo `campanha ` e removido automaticamente antes de localizar o template.
A coluna `etapa` e opcional; quando vazia, a pipeline assume `1`.
Linhas que tenham apenas o lote preenchido funcionam como cadastro visual e sao
ignoradas pelo worker, pois nao possuem data, horario e campanha.

O worker do EasyPanel inicia um cron dentro do container com
`TZ=America/Sao_Paulo`. O script `scripts/run_scheduled_campaign.py` le a
planilha, confere a data e o horario local e ignora qualquer linha fora do
momento programado.

Variaveis do worker:

```text
EMAIL_SCHEDULE_LIMIT=80
EMAIL_SCHEDULE_DRY_RUN=true
EMAIL_CRON_SCHEDULE=*/5 * * * *
EMAIL_SCHEDULE_SPREADSHEET_NAME=Cronograma Email MKT
EMAIL_SCHEDULE_SPREADSHEET_ID=
GOOGLE_SERVICE_ACCOUNT_FILE=mkt-novauniao-d64a259b4a40.json
GOOGLE_SERVICE_ACCOUNT_JSON=
GOOGLE_SERVICE_ACCOUNT_JSON_BASE64=
TZ=America/Sao_Paulo
```

Use `EMAIL_SCHEDULE_DRY_RUN=true` se quiser que o automatico simule sem enviar.

## Deploy em container no EasyPanel

O projeto pode rodar no EasyPanel usando o repositorio do GitHub como source e o `Dockerfile` deste projeto como builder. Com isso, o EasyPanel faz o build da imagem a partir do GitHub a cada deploy, sem precisar publicar manualmente em um registry.

Crie tres App Services apontando para o mesmo repositorio/branch:

```text
email-mkt-app      container principal para comandos manuais
email-mkt-worker   container com cron interno para disparos agendados
email-mkt-webhook  container HTTP para receber eventos da Resend
```

### Source e build

Nos dois servicos do EasyPanel:

```text
Source: GitHub
Repository: seu-owner/seu-repositorio
Branch: main
Build Path: /
Builder: Dockerfile
Dockerfile Path: Dockerfile
```

Se o repositorio for privado, configure o acesso do EasyPanel ao GitHub antes de criar os servicos.

### Servico principal

O comando padrao do `Dockerfile` inicia `scripts/docker/app.sh`. Esse container fica vivo para permitir execucoes manuais pelo console do EasyPanel:

```bash
python -m email_mkt.cli send --campaign 3formas-melhorar-experiencia --lote lote1 --limit 10 --dry-run
python -m email_mkt.cli send --campaign 3formas-melhorar-experiencia --lote lote1 --limit 50 --no-dry-run
```

No EasyPanel:

```text
Service: email-mkt-app
Source: GitHub
Builder: Dockerfile
Command: /app/scripts/docker/app.sh
```

### Worker com cron

O worker usa o mesmo repositorio e o mesmo `Dockerfile`, mas com outro comando de start:

```text
Service: email-mkt-worker
Source: GitHub
Builder: Dockerfile
Command: /app/scripts/docker/worker-cron.sh
```

Por padrao, o cron roda a cada 5 minutos em `America/Sao_Paulo` e o script
decide se ha campanha para a data/hora atual:

```env
EMAIL_CRON_SCHEDULE=*/5 * * * *
TZ=America/Sao_Paulo
```

O cron chama:

```bash
python scripts/run_scheduled_campaign.py
```

O script confere a data e o horario local em Sao Paulo e so executa linhas vencidas na planilha. Fora do horario programado, ele imprime uma mensagem e encerra sem enviar.

### Variaveis de ambiente no EasyPanel

Configure estas variaveis nos dois servicos:

```env
SUPABASE_DATABASE_URL=
SUPABASE_SCHEMA=mkt_novauniao
RESEND_API_KEY=
RESEND_WEBHOOK_SECRET=
EMAIL_FROM=Nova Uniao <contato@seudominio.com.br>
EMAIL_REPLY_TO=
EMAIL_BATCH_SIZE=50
RESEND_REQUESTS_PER_SECOND=1
DRY_RUN_DEFAULT=true
EMAIL_SCHEDULE_LIMIT=80
EMAIL_SCHEDULE_DRY_RUN=true
EMAIL_CRON_SCHEDULE=*/5 * * * *
EMAIL_SCHEDULE_SPREADSHEET_NAME=Cronograma Email MKT
EMAIL_SCHEDULE_SPREADSHEET_ID=
GOOGLE_SERVICE_ACCOUNT_FILE=mkt-novauniao-d64a259b4a40.json
GOOGLE_SERVICE_ACCOUNT_JSON=
GOOGLE_SERVICE_ACCOUNT_JSON_BASE64=
TZ=America/Sao_Paulo
```

Em producao, prefira configurar `GOOGLE_SERVICE_ACCOUNT_JSON_BASE64` como secret
com o JSON da service account codificado em Base64, ou montar o arquivo indicado
por `GOOGLE_SERVICE_ACCOUNT_FILE` dentro do container.

Para o primeiro deploy, mantenha:

```env
EMAIL_SCHEDULE_DRY_RUN=true
```

Depois de validar os logs, contatos, templates, opt-out e limites da Resend, habilite envio real no worker:

```env
EMAIL_SCHEDULE_DRY_RUN=false
```

## Proximas tarefas

- Definir as proximas datas, horarios, campanhas e limites de envio na planilha.
