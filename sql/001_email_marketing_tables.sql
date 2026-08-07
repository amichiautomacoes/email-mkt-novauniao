create table if not exists email_campaigns (
  id uuid primary key default gen_random_uuid(),
  campaign_key text not null unique,
  template_key text not null,
  status text not null default 'draft',
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create table if not exists email_campaign_recipients (
  id uuid primary key default gen_random_uuid(),
  campaign_id uuid not null references email_campaigns(id),
  contact_id text,
  email text not null,
  status text not null default 'pending',
  resend_email_id text,
  attempts integer not null default 0,
  last_error text,
  sent_at timestamptz,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create table if not exists email_send_events (
  id uuid primary key default gen_random_uuid(),
  provider text not null default 'resend',
  provider_message_id text,
  event_type text not null,
  payload jsonb not null default '{}'::jsonb,
  occurred_at timestamptz not null default now(),
  created_at timestamptz not null default now()
);

create table if not exists email_suppressions (
  id uuid primary key default gen_random_uuid(),
  email text not null unique,
  reason text not null,
  created_at timestamptz not null default now()
);

