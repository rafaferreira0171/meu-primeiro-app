-- LookLiP Finance — independent database schema
-- Run this in Supabase SQL editor after creating the project.

create table if not exists public.fluxo (
  id uuid primary key default gen_random_uuid(), user_id uuid not null references auth.users(id) on delete cascade,
  month text not null, salario numeric not null default 12000, va numeric not null default 700,
  condominio numeric not null default 975, iptu numeric not null default 145, gas numeric not null default 430,
  internet numeric not null default 90, luz numeric not null default 160, mercado numeric not null default 3000,
  combustivel numeric not null default 700, seguro_carro numeric not null default 250, convenio numeric not null default 1651,
  cartao numeric not null default 1718, celular numeric not null default 69, cabelo numeric not null default 75,
  academia numeric not null default 149, contabilidade numeric not null default 250, pernambucanas numeric not null default 71,
  assin_chat numeric not null default 45, assin_apple numeric not null default 8, assin_ifood numeric not null default 19,
  assin_uber numeric not null default 19, outros numeric not null default 153, unique(user_id, month)
);
create table if not exists public.empregada (
  id uuid primary key default gen_random_uuid(), user_id uuid not null references auth.users(id) on delete cascade,
  month text not null, salario numeric not null default 1400, dias_uteis numeric not null default 40,
  passagem_scs numeric not null default 5, passagem_sp numeric not null default 5.9, unique(user_id, month)
);
create table if not exists public.prestador (
  id uuid primary key default gen_random_uuid(), user_id uuid not null references auth.users(id) on delete cascade,
  prestador_id uuid, month text not null, nome text not null,
  salario numeric not null default 1400, dias_uteis numeric not null default 40,
  passagem_scs numeric not null default 5, passagem_sp numeric not null default 5.9,
  ativo boolean not null default true
);
create table if not exists public.entrada (
  id uuid primary key default gen_random_uuid(), user_id uuid not null references auth.users(id) on delete cascade,
  series_id uuid, month text not null, nome text not null, valor numeric not null default 0,
  ativo boolean not null default true
);
create table if not exists public.despesa (
  id uuid primary key default gen_random_uuid(), user_id uuid not null references auth.users(id) on delete cascade,
  series_id uuid, month text not null, nome text not null, valor numeric not null default 0,
  ativo boolean not null default true
);
create table if not exists public.gasto (
  id uuid primary key default gen_random_uuid(), user_id uuid not null references auth.users(id) on delete cascade,
  month text not null, conta text not null, budget_account_id uuid,
  valor numeric not null default 0, is_ajuste boolean not null default false
);
create table if not exists public.transferencia (
  id uuid primary key default gen_random_uuid(), user_id uuid not null references auth.users(id) on delete cascade,
  series_id uuid, month text not null, nome text not null, items jsonb not null default '[]'::jsonb,
  ativo boolean not null default true
);
create table if not exists public.budget_account (
  id uuid primary key default gen_random_uuid(), user_id uuid not null references auth.users(id) on delete cascade,
  month text not null, nome text not null, budget numeric not null default 0,
  legacy_key text, ativo boolean not null default true
);

-- Safe upgrades for an already-created Supabase project.
alter table public.prestador add column if not exists prestador_id uuid;
alter table public.prestador add column if not exists ativo boolean not null default true;
alter table public.entrada add column if not exists series_id uuid;
alter table public.entrada add column if not exists ativo boolean not null default true;
alter table public.despesa add column if not exists series_id uuid;
alter table public.despesa add column if not exists ativo boolean not null default true;
alter table public.transferencia add column if not exists series_id uuid;
alter table public.transferencia add column if not exists ativo boolean not null default true;
alter table public.gasto add column if not exists budget_account_id uuid;
alter table public.gasto drop constraint if exists gasto_conta_check;
alter table public.budget_account add column if not exists legacy_key text;
alter table public.budget_account add column if not exists ativo boolean not null default true;

-- Per-user onboarding state. The first authenticated session is anchored to its current month.
create table if not exists public.user_settings (
  user_id uuid primary key references auth.users(id) on delete cascade,
  start_month text not null,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);
alter table public.user_settings enable row level security;
drop policy if exists "Users manage own user_settings" on public.user_settings;
create policy "Users manage own user_settings" on public.user_settings for all using (auth.uid() = user_id) with check (auth.uid() = user_id);
create index if not exists user_settings_user_idx on public.user_settings(user_id);

alter table public.fluxo enable row level security;
alter table public.empregada enable row level security;
alter table public.prestador enable row level security;
alter table public.entrada enable row level security;
alter table public.despesa enable row level security;
alter table public.gasto enable row level security;
alter table public.transferencia enable row level security;
alter table public.budget_account enable row level security;

create policy "Users manage own fluxo" on public.fluxo for all using (auth.uid() = user_id) with check (auth.uid() = user_id);
create policy "Users manage own empregada" on public.empregada for all using (auth.uid() = user_id) with check (auth.uid() = user_id);
create policy "Users manage own prestador" on public.prestador for all using (auth.uid() = user_id) with check (auth.uid() = user_id);
create policy "Users manage own entrada" on public.entrada for all using (auth.uid() = user_id) with check (auth.uid() = user_id);
create policy "Users manage own despesa" on public.despesa for all using (auth.uid() = user_id) with check (auth.uid() = user_id);
create policy "Users manage own gasto" on public.gasto for all using (auth.uid() = user_id) with check (auth.uid() = user_id);
create policy "Users manage own transferencia" on public.transferencia for all using (auth.uid() = user_id) with check (auth.uid() = user_id);
create policy "Users manage own budget_account" on public.budget_account for all using (auth.uid() = user_id) with check (auth.uid() = user_id);

create index if not exists fluxo_user_month_idx on public.fluxo(user_id, month);
create index if not exists empregada_user_month_idx on public.empregada(user_id, month);
create index if not exists prestador_user_month_idx on public.prestador(user_id, month);
create index if not exists entrada_user_month_idx on public.entrada(user_id, month);
create index if not exists despesa_user_month_idx on public.despesa(user_id, month);
create index if not exists gasto_user_month_idx on public.gasto(user_id, month);
create index if not exists transferencia_user_month_idx on public.transferencia(user_id, month);
create index if not exists budget_account_user_month_idx on public.budget_account(user_id, month);
