create table if not exists mkt_novauniao.email_mkt_envio (
  email text primary key,
  data_envio timestamptz not null default now(),
  campanha text not null,
  numero_envios integer not null default 0
);
