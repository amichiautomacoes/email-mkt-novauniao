# Email Marketing Pipeline

Pipeline para sincronizar contatos no Supabase, renderizar templates HTML e disparar emails via Resend com controle de limites.

## Estrutura

```text
templates/raw/       HTMLs originais
templates/clean/     HTMLs tratados e prontos para envio
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
python -m email_mkt.cli send --campaign lote2 --limit 10 --dry-run
```

Por padrao, a pipeline nasce em modo seguro. O envio real so deve ser habilitado depois de validar contatos, templates, opt-out e limites do Resend.

## Lotes e templates

As campanhas por lote usam a coluna `lote` da tabela `mkt_novauniao.email_mkt` e respeitam o limite informado em `--limit`.

```text
lote1 -> 3formas-melhorar-experiencia
lote2 -> etiquetas-ideais
lote3 -> segredo-sistema
lote4 -> detalhe-loja
lote5 -> 3formas-melhorar-experiencia
```

Exemplo:

```powershell
python -m email_mkt.cli send --campaign lote1 --limit 50 --dry-run
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
python -m email_mkt.cli send --campaign lote1 --limit 50 --no-dry-run
```

## Controle de envio

Os envios reais aceitos pela Resend sao registrados em `mkt_novauniao.email_controle_envio`:

```text
email          chave primaria
data_envio     ultima data de envio
campanha       ultima campanha/lote enviado
numero_envios  contador acumulado de envios aceitos
```

Execucoes em `--dry-run` nao gravam nessa tabela.

## GitHub Actions

O workflow `.github/workflows/email-disparos.yml` permite disparos manuais pela aba Actions do GitHub.

Configure estes secrets no repositorio:

```text
SUPABASE_DATABASE_URL
SUPABASE_SCHEMA
RESEND_API_KEY
EMAIL_FROM
EMAIL_REPLY_TO
EMAIL_BATCH_SIZE
RESEND_REQUESTS_PER_SECOND
```

No primeiro teste pelo GitHub, use `dry_run=true`, `campaign=lote1` e `limit=2`.

### Programacao automatica

As campanhas abaixo estao programadas para 09:30 no horario de Sao Paulo:

```text
2026-08-10 lote1 -> 3formas-melhorar-experiencia
2026-08-11 lote2 -> etiquetas-ideais
2026-08-12 lote3 -> segredo-sistema
2026-08-13 lote4 -> detalhe-loja
2026-08-14 lote5 -> 3formas-melhorar-experiencia
```

O cron do GitHub roda em UTC, por isso o workflow usa `30 12 10-14 8 *`. O script `scripts/run_scheduled_campaign.py` confere a data em `America/Sao_Paulo` e ignora qualquer data fora da programacao de 2026.

Variaveis opcionais do repositorio:

```text
EMAIL_SCHEDULE_LIMIT=80
EMAIL_SCHEDULE_DRY_RUN=false
```

Use `EMAIL_SCHEDULE_DRY_RUN=true` se quiser que o automatico simule sem enviar.

## Proximas tarefas

- Organizar nomes de campanhas e lotes para deixar a operacao mais clara do que `lote1`, `lote2`, etc.
- Sincronizar os horarios de disparo com uma planilha no Google Sheets/Drive, usando a planilha como fonte de verdade para datas, campanhas, limites e modo dry-run.
- Criar um formato de execucao em container para EasyPanel, com variaveis de ambiente, comando de start e estrategia de agendamento/cron.
