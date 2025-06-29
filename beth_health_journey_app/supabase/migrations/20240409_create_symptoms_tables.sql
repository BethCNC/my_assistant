-- Create symptoms table
CREATE OR REPLACE FUNCTION public.create_symptoms_table()
RETURNS void
LANGUAGE plpgsql
AS $$
BEGIN
  CREATE TABLE IF NOT EXISTS public.symptoms (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    condition_id UUID REFERENCES public.conditions(id),
    name TEXT NOT NULL,
    description TEXT,
    severity INTEGER CHECK (severity >= 0 AND severity <= 10),
    frequency TEXT,
    duration TEXT,
    triggers TEXT[],
    alleviating_factors TEXT[],
    date_recorded TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
  );

  -- Create medical_event_symptoms table for many-to-many relationship
  CREATE TABLE IF NOT EXISTS public.medical_event_symptoms (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    medical_event_id UUID REFERENCES public.medical_events(id) ON DELETE CASCADE,
    symptom_id UUID REFERENCES public.symptoms(id) ON DELETE CASCADE,
    severity INTEGER CHECK (severity >= 0 AND severity <= 10),
    notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(medical_event_id, symptom_id)
  );

  -- Add RLS policies
  ALTER TABLE public.symptoms ENABLE ROW LEVEL SECURITY;
  ALTER TABLE public.medical_event_symptoms ENABLE ROW LEVEL SECURITY;

  -- Create policies
  CREATE POLICY "Enable read access for authenticated users" ON public.symptoms
    FOR SELECT
    TO authenticated
    USING (true);

  CREATE POLICY "Enable insert access for authenticated users" ON public.symptoms
    FOR INSERT
    TO authenticated
    WITH CHECK (true);

  CREATE POLICY "Enable update access for authenticated users" ON public.symptoms
    FOR UPDATE
    TO authenticated
    USING (true)
    WITH CHECK (true);

  CREATE POLICY "Enable delete access for authenticated users" ON public.symptoms
    FOR DELETE
    TO authenticated
    USING (true);

  -- Medical event symptoms policies
  CREATE POLICY "Enable read access for authenticated users" ON public.medical_event_symptoms
    FOR SELECT
    TO authenticated
    USING (true);

  CREATE POLICY "Enable insert access for authenticated users" ON public.medical_event_symptoms
    FOR INSERT
    TO authenticated
    WITH CHECK (true);

  CREATE POLICY "Enable update access for authenticated users" ON public.medical_event_symptoms
    FOR UPDATE
    TO authenticated
    USING (true)
    WITH CHECK (true);

  CREATE POLICY "Enable delete access for authenticated users" ON public.medical_event_symptoms
    FOR DELETE
    TO authenticated
    USING (true);
END;
$$;

-- Create medical_event_symptoms table function
CREATE OR REPLACE FUNCTION public.create_medical_event_symptoms_table()
RETURNS void
LANGUAGE plpgsql
AS $$
BEGIN
  -- This is handled in the create_symptoms_table function
  -- but we keep this for compatibility with existing code
  NULL;
END;
$$; 