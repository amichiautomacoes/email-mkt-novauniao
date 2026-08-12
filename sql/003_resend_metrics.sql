create table if not exists mkt_novauniao.email_mkt_metricas (
  id uuid primary key default gen_random_uuid(),
  source text not null default 'resend_metrics_api',
  fetched_at timestamptz not null default now(),
  start_date timestamptz,
  end_date timestamptz,
  timezone text not null default 'America/Sao_Paulo',
  granularity text not null default 'daily',
  metrics text[] not null default '{}',
  dimensions text[] not null default '{}',
  totals jsonb not null default '{}'::jsonb,
  data jsonb not null default '[]'::jsonb,
  svix_id text,
  event_type text,
  event_created_at timestamptz,
  webhook_received_at timestamptz,
  resend_email_id text,
  message_id text,
  recipient_email text,
  subject text,
  campaign_key text,
  template_key text,
  lote_key text,
  raw_payload jsonb not null default '{}'::jsonb
);

create index if not exists idx_email_mkt_metricas_fetched_at
  on mkt_novauniao.email_mkt_metricas (fetched_at desc);

create unique index if not exists idx_email_mkt_metricas_svix_id
  on mkt_novauniao.email_mkt_metricas (svix_id)
  where svix_id is not null;

create index if not exists idx_email_mkt_metricas_event_created_at
  on mkt_novauniao.email_mkt_metricas (event_created_at desc)
  where event_created_at is not null;

create index if not exists idx_email_mkt_metricas_event_type
  on mkt_novauniao.email_mkt_metricas (event_type)
  where event_type is not null;

alter table mkt_novauniao.email_mkt_metricas
  drop constraint if exists chk_email_mkt_metricas_webhook_event_type;

alter table mkt_novauniao.email_mkt_metricas
  add constraint chk_email_mkt_metricas_webhook_event_type
  check (
    source <> 'resend_webhook'
    or event_type in (
      'email.bounced',
      'email.clicked',
      'email.complained',
      'email.opened'
    )
  );

create or replace function mkt_novauniao.remover_lead_email_mkt_rejeitado()
returns trigger
language plpgsql
as $$
declare
  email_rejeitado text;
begin
  if new.source = 'resend_webhook'
     and new.event_type in ('email.bounced', 'email.complained') then
    email_rejeitado := coalesce(
      nullif(btrim(new.recipient_email), ''),
      nullif(btrim(new.raw_payload #>> '{data,to,0}'), '')
    );

    if email_rejeitado is not null then
      delete from mkt_novauniao.email_mkt_leads
      where lower(email) = lower(email_rejeitado);
    end if;
  end if;

  return new;
end;
$$;

drop trigger if exists trg_email_mkt_metricas_remover_lead_rejeitado
  on mkt_novauniao.email_mkt_metricas;

create trigger trg_email_mkt_metricas_remover_lead_rejeitado
after insert on mkt_novauniao.email_mkt_metricas
for each row
execute function mkt_novauniao.remover_lead_email_mkt_rejeitado();
