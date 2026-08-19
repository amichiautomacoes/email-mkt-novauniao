create extension if not exists pgcrypto;

alter table mkt_novauniao.email_mkt_envio
  add column if not exists email_norm text
    generated always as (lower(btrim(email))) stored,
  add column if not exists lote_key text,
  add column if not exists etapa integer not null default 1 check (etapa >= 1),
  add column if not exists template_key text;

alter table mkt_novauniao.email_mkt_envio_historico
  drop constraint if exists email_mkt_envio_historico_status_check;

alter table mkt_novauniao.email_mkt_envio_historico
  add constraint email_mkt_envio_historico_status_check
  check (status in ('accepted', 'failed', 'duplicate'));

with ranked as (
  select
    id,
    row_number() over (
      partition by email_norm, lote_key
      order by data_envio, id
    ) as lote_rank
  from mkt_novauniao.email_mkt_envio_historico
  where status = 'accepted'
    and lote_key is not null
)
update mkt_novauniao.email_mkt_envio_historico as history
set
  status = 'duplicate',
  resend_response = history.resend_response || jsonb_build_object(
    'deduplicated_at', now(),
    'dedupe_reason', 'duplicate accepted send for same email/lote'
  )
from ranked
where ranked.id = history.id
  and ranked.lote_rank > 1;

drop index if exists mkt_novauniao.email_mkt_envio_hist_lote_etapa_uidx;

create unique index if not exists email_mkt_envio_hist_lote_uidx
  on mkt_novauniao.email_mkt_envio_historico (email_norm, lote_key)
  where status = 'accepted' and lote_key is not null;

create index if not exists email_mkt_envio_hist_lote_idx
  on mkt_novauniao.email_mkt_envio_historico (lote_key, data_envio)
  where status = 'accepted' and lote_key is not null;

with latest_history as (
  select distinct on (email_norm)
    email_norm,
    lote_key,
    etapa,
    template_key,
    campanha
  from mkt_novauniao.email_mkt_envio_historico
  where status = 'accepted'
  order by email_norm, data_envio desc, id desc
)
update mkt_novauniao.email_mkt_envio as envio
set
  lote_key = latest_history.lote_key,
  etapa = latest_history.etapa,
  template_key = latest_history.template_key,
  campanha = latest_history.campanha
from latest_history
where latest_history.email_norm = envio.email_norm;

create index if not exists email_mkt_envio_lote_idx
  on mkt_novauniao.email_mkt_envio (lote_key, data_envio desc)
  where lote_key is not null;
