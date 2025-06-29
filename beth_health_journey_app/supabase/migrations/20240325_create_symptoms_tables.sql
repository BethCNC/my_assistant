-- Create symptoms table
create or replace function public.create_symptoms_table()
returns void
language plpgsql
security definer
as $$
begin
  create table if not exists public.symptoms (
    id uuid primary key default uuid_generate_v4(),
    name text not null,
    description text,
    created_at timestamp with time zone default timezone('utc'::text, now()) not null,
    updated_at timestamp with time zone default timezone('utc'::text, now()) not null
  );

  -- Add RLS policies
  alter table public.symptoms enable row level security;

  create policy "Enable read access for authenticated users"
    on public.symptoms for select
    using (auth.role() = 'authenticated');

  create policy "Enable insert for authenticated users"
    on public.symptoms for insert
    with check (auth.role() = 'authenticated');

  create policy "Enable update for authenticated users"
    on public.symptoms for update
    using (auth.role() = 'authenticated')
    with check (auth.role() = 'authenticated');
end;
$$;

-- Create medical_event_symptoms table
create or replace function public.create_medical_event_symptoms_table()
returns void
language plpgsql
security definer
as $$
begin
  create table if not exists public.medical_event_symptoms (
    id uuid primary key default uuid_generate_v4(),
    medical_event_id uuid references public.medical_events(id) on delete cascade,
    symptom_id uuid references public.symptoms(id) on delete cascade,
    severity integer check (severity between 1 and 10),
    notes text,
    created_at timestamp with time zone default timezone('utc'::text, now()) not null,
    updated_at timestamp with time zone default timezone('utc'::text, now()) not null,
    unique(medical_event_id, symptom_id)
  );

  -- Add RLS policies
  alter table public.medical_event_symptoms enable row level security;

  create policy "Enable read access for authenticated users"
    on public.medical_event_symptoms for select
    using (auth.role() = 'authenticated');

  create policy "Enable insert for authenticated users"
    on public.medical_event_symptoms for insert
    with check (auth.role() = 'authenticated');

  create policy "Enable update for authenticated users"
    on public.medical_event_symptoms for update
    using (auth.role() = 'authenticated')
    with check (auth.role() = 'authenticated');
end;
$$; 