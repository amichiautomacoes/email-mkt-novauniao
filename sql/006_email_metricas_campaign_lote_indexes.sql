create index if not exists idx_email_mkt_metricas_campaign_lote_event
  on mkt_novauniao.email_mkt_metricas (
    campaign_key,
    lote_key,
    event_type,
    event_created_at desc
  )
  where source = 'resend_webhook';

create index if not exists idx_email_mkt_metricas_template_event
  on mkt_novauniao.email_mkt_metricas (
    template_key,
    event_type,
    event_created_at desc
  )
  where source = 'resend_webhook';

create index if not exists idx_email_mkt_metricas_recipient_event
  on mkt_novauniao.email_mkt_metricas (
    lower(btrim(recipient_email)),
    event_type,
    event_created_at desc
  )
  where source = 'resend_webhook'
    and recipient_email is not null;
